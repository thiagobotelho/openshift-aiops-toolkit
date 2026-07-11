import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class SecurityStaticTests(unittest.TestCase):
    def test_no_shell_true_literal_in_code(self):
        needle='shell' + '=True'
        for path in list((ROOT/'mcp_server').rglob('*.py')) + list((ROOT/'scripts').rglob('*.sh')):
            self.assertNotIn(needle, path.read_text(encoding='utf-8'))
    def test_no_generic_mcp_tool_names(self):
        text='\n'.join(path.read_text(encoding='utf-8') for path in (ROOT/'mcp_server').rglob('*.py'))
        for name in ['execute_command','execute_shell','run_command','run_kubectl','run_bash']:
            self.assertNotIn(f'"{name}"', text); self.assertNotIn(f"'{name}'", text)
    def test_no_secret_collection_commands_in_scripts(self):
        patterns=['get secret','get secrets','describe secret']
        for path in (ROOT/'scripts').rglob('*.sh'):
            text=path.read_text(encoding='utf-8').lower()
            for pattern in patterns: self.assertNotIn(pattern, text)
    def test_blocked_catalog_exists(self):
        text=(ROOT/'config'/'allowed-commands.yaml').read_text(encoding='utf-8')
        for word in ['delete','patch','debug','port-forward']:
            self.assertIn(word, text)
if __name__ == '__main__': unittest.main()
