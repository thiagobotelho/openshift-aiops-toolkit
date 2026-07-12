import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import subprocess

from mcp_server.models import CommandResult
from mcp_server.must_gather import analyze_must_gather, collect_preflight, execute_must_gather, gitignore_covers_evidence


class MustGatherTests(unittest.TestCase):
    def test_gitignore_covers_evidence(self):
        self.assertTrue(gitignore_covers_evidence())

    def test_preflight_detects_supported_options(self):
        help_result = CommandResult(
            ["oc", "adm", "must-gather", "--help"],
            0,
            "Usage\n  --dest-dir string\n  --all-images=false\n  --volume-percentage int\n",
            "",
            0.01,
        )
        generic = CommandResult(["oc"], 0, "ok", "", 0.01)
        with tempfile.TemporaryDirectory() as tmp, patch("mcp_server.must_gather.run_oc", side_effect=[help_result, generic, generic, generic, generic, generic, generic, generic, generic]), patch("mcp_server.must_gather.run_host_command", return_value={"exit_code": 0}):
            payload = collect_preflight("crc-lab", 10, tmp)
        self.assertTrue(payload["supported_options"]["dest_dir"])
        self.assertTrue(payload["supported_options"]["all_images"])
        self.assertIn("planned_oc_args", payload)

    def test_execute_must_gather_writes_manifest_and_marker(self):
        help_result = CommandResult(
            ["oc", "adm", "must-gather", "--help"],
            0,
            "Usage\n  --dest-dir string\n  --all-images=false\n",
            "",
            0.01,
        )
        generic = CommandResult(["oc"], 0, "ok", "", 0.01)
        completed = subprocess.CompletedProcess(["oc"], 0, "stdout", "stderr")
        with tempfile.TemporaryDirectory() as tmp, patch("mcp_server.must_gather.run_oc", side_effect=[help_result, generic, generic, generic, generic, generic, generic, generic, generic, generic]), patch("mcp_server.must_gather.run_host_command", return_value={"exit_code": 0}), patch("subprocess.run", return_value=completed):
            output = execute_must_gather(cluster="crc-lab", output_dir=tmp, timeout=10)
            self.assertTrue((output / "DO-NOT-COMMIT.txt").exists())
            self.assertTrue((output / "metadata" / "manifest.json").exists())
            self.assertTrue((output / "metadata" / "checksums.sha256").exists())

    def test_analyze_must_gather_writes_security_findings_without_changing_raw(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "must-gather"
            raw = base / "raw"
            raw.mkdir(parents=True)
            raw_file = raw / "sample.txt"
            raw_file.write_text("Authorization: Bearer abc.def.ghi\n", encoding="utf-8")
            before = raw_file.read_text(encoding="utf-8")
            report = analyze_must_gather(base)
            after = raw_file.read_text(encoding="utf-8")
        self.assertEqual(before, after)
        self.assertTrue(report.name.endswith(".md"))


if __name__ == "__main__":
    unittest.main()
