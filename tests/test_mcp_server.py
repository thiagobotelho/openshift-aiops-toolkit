import json
import subprocess
import sys
import unittest
from unittest.mock import patch

from mcp_server.models import CommandResult
from mcp_server.tools import call_tool, list_tools
from mcp_server.validators import ValidationError


class McpServerProtocolTests(unittest.TestCase):
    def test_stdio_initialize_and_list_tools_returns_specific_schemas(self):
        messages = [
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "unittest", "version": "0.0.0"},
                },
            },
            {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        ]
        proc = subprocess.run(
            [sys.executable, "-m", "mcp_server.server"],
            input="\n".join(json.dumps(message) for message in messages) + "\n",
            text=True,
            capture_output=True,
            timeout=8,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        responses = [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]
        self.assertGreaterEqual(len(responses), 2)
        tools = responses[-1]["result"]["tools"]
        self.assertTrue(tools)
        self.assertIn("inputSchema", tools[0])
        self.assertNotEqual(list(tools[0]["inputSchema"].get("properties", {})), ["arguments"])

    def test_tool_schemas_accept_common_readonly_parameters(self):
        tools = {tool["name"]: tool for tool in list_tools()}
        schema = tools["cluster_identity"]["inputSchema"]
        self.assertIn("environment", schema["properties"])
        self.assertIn("cluster", schema["properties"])
        self.assertIn("timeout", schema["properties"])
        self.assertFalse(schema["additionalProperties"])

    def test_tool_call_accepts_common_parameters(self):
        result = CommandResult(["oc", "config", "current-context"], 0, "crc\n", "", 0.01)
        with patch("mcp_server.context.run_oc", return_value=result):
            payload = call_tool("current_context", {"environment": "laboratory", "cluster": "crc-lab", "timeout": 5})
        self.assertEqual(payload["exit_code"], 0)

    def test_tool_call_blocks_production_without_confirmation(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ValidationError):
                call_tool("list_configured_clusters", {"environment": "production", "cluster": "prod"})
            payload = call_tool(
                "list_configured_clusters",
                {"environment": "production", "cluster": "prod", "confirm_production": "prod"},
            )
        self.assertIn("clusters", payload)

    def test_tool_call_respects_environment_variables_for_production(self):
        with patch.dict("os.environ", {"OPENSHIFT_AIOPS_ENVIRONMENT": "production", "OPENSHIFT_AIOPS_CLUSTER": "prod"}, clear=True):
            with self.assertRaises(ValidationError):
                call_tool("list_configured_clusters", {})
        with patch.dict(
            "os.environ",
            {
                "OPENSHIFT_AIOPS_ENVIRONMENT": "production",
                "OPENSHIFT_AIOPS_CLUSTER": "prod",
                "OPENSHIFT_AIOPS_PRODUCTION_CONFIRM": "prod",
            },
            clear=True,
        ):
            payload = call_tool("list_configured_clusters", {})
        self.assertIn("clusters", payload)


if __name__ == "__main__":
    unittest.main()
