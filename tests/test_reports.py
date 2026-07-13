import json
import tempfile
import unittest
from pathlib import Path

from mcp_server.reports import generate_base_report


class ReportTests(unittest.TestCase):
    def test_report_contains_sections(self):
        report=generate_base_report(title='Teste')
        self.assertIn('# Teste', report)
        self.assertIn('Resumo executivo', report)
        self.assertIn('Achados priorizados', report)
        self.assertIn('Detalhamento dos achados', report)

    def test_report_lists_each_error_with_probable_cause_and_resolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "operators").mkdir()
            (base / "cluster").mkdir()
            (base / "workloads").mkdir()
            clusteroperators = {
                "command": ["oc", "get", "clusteroperators", "-o", "json"],
                "exit_code": 0,
                "stdout": json.dumps(
                    {
                        "items": [
                            {
                                "metadata": {"name": "authentication"},
                                "status": {
                                    "conditions": [
                                        {
                                            "type": "Degraded",
                                            "status": "True",
                                            "reason": "OAuthServerRouteEndpointAccessibleControllerDegraded",
                                            "message": "route endpoint is not reachable",
                                        }
                                    ]
                                },
                            }
                        ]
                    }
                ),
                "stderr": "",
                "duration_seconds": 0.1,
                "timed_out": False,
                "truncated": False,
            }
            pods_not_running = {
                "command": ["oc", "get", "pods", "-A"],
                "exit_code": 1,
                "stdout": "",
                "stderr": "Error from server (Forbidden): pods is forbidden",
                "duration_seconds": 0.1,
                "timed_out": False,
                "truncated": False,
            }
            (base / "operators" / "clusteroperators.json").write_text(json.dumps(clusteroperators), encoding="utf-8")
            (base / "workloads" / "pods-not-running.json").write_text(json.dumps(pods_not_running), encoding="utf-8")
            manifest = {
                "cluster": "crc-lab",
                "environment": "current",
                "context": "crc-admin",
                "commands": [
                    {"name": "clusteroperators", "command": clusteroperators["command"], "exit_code": 0},
                    {"name": "pods-not-running", "command": pods_not_running["command"], "exit_code": 1},
                ],
                "files": [
                    {"path": "operators/clusteroperators.json", "sha256": "x", "size_bytes": 1},
                    {"path": "workloads/pods-not-running.json", "sha256": "y", "size_bytes": 1},
                ],
            }
            (base / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            report = generate_base_report(base, title="Diagnóstico")
        self.assertIn("ACH-001", report)
        self.assertIn("ClusterOperator `authentication` está Degraded=True", report)
        self.assertIn("Comando `pods-not-running` retornou exit code 1", report)
        self.assertIn("Causa provável", report)
        self.assertIn("Como validar", report)
        self.assertIn("Como resolver", report)


if __name__ == '__main__': unittest.main()
