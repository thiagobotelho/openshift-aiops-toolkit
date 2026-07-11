import unittest
from mcp_server import config
from mcp_server.context import list_configured_clusters, select_cluster_context
class ContextTests(unittest.TestCase):
    def test_inventory_loads(self):
        clusters=list_configured_clusters()
        self.assertTrue(any(c['name']=='cluster-dev' for c in clusters))
    def test_select_cluster_does_not_switch(self):
        selected=select_cluster_context('cluster-dev')
        self.assertTrue(selected['found']); self.assertIn('não troca contexto', selected['message'])
    def test_version(self):
        self.assertRegex(config.version(), r'^\d+\.\d+\.\d+')
if __name__ == '__main__': unittest.main()
