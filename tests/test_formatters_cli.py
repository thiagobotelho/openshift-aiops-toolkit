import json
import subprocess
import sys
import unittest
from unittest.mock import patch

from mcp_server.cli import main as cli_main, response_for_command
from mcp_server.capabilities import has_resource
from mcp_server.formatters import render_response, status_label, table
from mcp_server.models import CommandResult
from mcp_server.schemas import ClusterIdentity, ToolResponse


class FormatterAndCliTests(unittest.TestCase):
    def test_status_labels_have_ascii_fallback(self):
        self.assertEqual(status_label("ok", ascii_only=True), "[OK]")
        self.assertIn("ALERTA", status_label("warning", ascii_only=True))

    def test_table_renders_headers(self):
        rendered = table(["NOME", "STATUS"], [["authentication", "ok"]], max_width=120)
        self.assertIn("NOME", rendered)
        self.assertIn("authentication", rendered)

    def test_metrics_api_resource_detection_uses_api_group(self):
        resources = "pods   metrics.k8s.io/v1beta1   true   PodMetrics\n"
        self.assertTrue(has_resource(resources, "pods", "metrics.k8s.io"))
        self.assertFalse(has_resource(resources, "pods", "other.group"))

    def test_json_render_has_schema_version(self):
        response = ToolResponse(tool="health", summary="ok", cluster=ClusterIdentity(name="crc"))
        payload = json.loads(render_response(response, output="json"))
        self.assertEqual(payload["schema_version"], "1.0")
        self.assertEqual(payload["cluster"]["name"], "crc")

    def test_markdown_render(self):
        response = ToolResponse(tool="health", summary="ok", cluster=ClusterIdentity(name="crc"))
        rendered = render_response(response, output="markdown")
        self.assertIn("# health", rendered)
        self.assertIn("crc", rendered)

    def test_root_cli_help_does_not_require_cluster(self):
        proc = subprocess.run(["./openshift-aiops", "--help"], text=True, capture_output=True, timeout=5, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("OpenShift AIOps Toolkit", proc.stdout)

    def test_cli_health_with_mocked_oc(self):
        def fake_run_oc(args, **kwargs):
            if args == ["config", "current-context"]:
                return CommandResult(["oc", *args], 0, "crc-admin\n", "", 0.01)
            if args == ["whoami"]:
                return CommandResult(["oc", *args], 0, "kubeadmin\n", "", 0.01)
            if args == ["whoami", "--show-server"]:
                return CommandResult(["oc", *args], 0, "https://api.crc.testing:6443\n", "", 0.01)
            if args == ["version"]:
                return CommandResult(["oc", *args], 0, "Server Version: 4.22.1\n", "", 0.01)
            if args == ["get", "infrastructure", "cluster", "-o", "json"]:
                return CommandResult(["oc", *args], 0, '{"status":{"infrastructureName":"crc","platform":"None","controlPlaneTopology":"SingleReplica","infrastructureTopology":"SingleReplica"}}', "", 0.01)
            if args == ["get", "nodes", "-o", "json"]:
                return CommandResult(["oc", *args], 0, '{"items":[{"metadata":{"name":"crc"}}]}', "", 0.01)
            if args == ["get", "network.config.openshift.io", "cluster", "-o", "json"]:
                return CommandResult(["oc", *args], 0, '{"status":{"networkType":"OVNKubernetes"}}', "", 0.01)
            if args == ["get", "clusteroperators", "-o", "json"]:
                return CommandResult(["oc", *args], 0, '{"items":[]}', "", 0.01)
            if args == ["get", "pods", "-A", "--field-selector=status.phase!=Running", "-o", "wide"]:
                return CommandResult(["oc", *args], 0, "NAMESPACE NAME STATUS\n", "", 0.01)
            if args == ["api-resources"]:
                return CommandResult(["oc", *args], 0, "pods\nroutes\nclusteroperators\n", "", 0.01)
            if args == ["api-versions"]:
                return CommandResult(["oc", *args], 0, "v1\nroute.openshift.io/v1\n", "", 0.01)
            return CommandResult(["oc", *args], 0, "", "", 0.01)

        with patch("mcp_server.cli.run_oc", side_effect=fake_run_oc), patch("mcp_server.capabilities.run_oc", side_effect=fake_run_oc), patch("mcp_server.cli.detect_cluster_name", return_value="crc"):
            response = response_for_command("health", argparse_namespace())
        self.assertEqual(response.execution_status, "success")
        self.assertEqual(response.cluster.name, "crc")
        self.assertIsInstance(response.data["capabilities"], list)


def argparse_namespace():
    class Args:
        timeout = 5
        context = None
        kubeconfig = None
    return Args()


if __name__ == "__main__":
    unittest.main()
