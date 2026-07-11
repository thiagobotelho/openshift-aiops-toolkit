import tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from mcp_server.collectors import collect_cluster_evidence
from mcp_server.models import CommandResult
class CollectorTests(unittest.TestCase):
    def test_collect_cluster_with_mocked_oc(self):
        fake=CommandResult(['oc','get'],0,'{}','',0.01)
        with tempfile.TemporaryDirectory() as tmp, patch('mcp_server.collectors.run_oc', return_value=fake):
            output=collect_cluster_evidence(cluster='cluster-dev', environment='development', output_dir=Path(tmp))
            self.assertTrue((output/'manifest.json').exists())
            self.assertTrue((output/'checksums.sha256').exists())
if __name__ == '__main__': unittest.main()
