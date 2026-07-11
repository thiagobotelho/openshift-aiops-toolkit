import subprocess, unittest
from unittest.mock import patch
from mcp_server.commands import CommandBlocked, run_oc, validate_oc_args
class CommandsTests(unittest.TestCase):
    def test_blocks_mutating_oc(self):
        for args in [['delete','pod','x'], ['patch','deployment','x'], ['adm','drain','node-a']]:
            with self.assertRaises(CommandBlocked): validate_oc_args(args)
    def test_blocks_secret_content(self):
        with self.assertRaises(CommandBlocked): validate_oc_args(['get','secrets'])
    def test_allows_readonly(self):
        validate_oc_args(['get','pods','-A','-o','wide']); validate_oc_args(['auth','can-i','--list'])
    def test_subprocess_uses_argument_list(self):
        completed=subprocess.CompletedProcess(['oc','version'],0,'ok','')
        with patch('subprocess.run', return_value=completed) as mocked:
            result=run_oc(['version'])
        self.assertIsInstance(mocked.call_args.args[0], list)
        self.assertIsNot(mocked.call_args.kwargs.get('shell'), True)
        self.assertEqual(result.exit_code, 0)
if __name__ == '__main__': unittest.main()
