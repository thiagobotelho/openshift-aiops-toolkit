import unittest
from mcp_server.reports import generate_base_report
class ReportTests(unittest.TestCase):
    def test_report_contains_sections(self):
        report=generate_base_report(title='Teste')
        self.assertIn('# Teste', report); self.assertIn('Resumo executivo', report); self.assertIn('Achados', report)
if __name__ == '__main__': unittest.main()
