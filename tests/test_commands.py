import argparse, io, subprocess, unittest
from contextlib import redirect_stdout
from unittest.mock import patch
from mcp_server.commands import CommandBlocked, build_oc_command, command_prefix, preflight, require_production_confirmation, run_oc, validate_oc_args
from mcp_server.validators import ValidationError
class CommandsTests(unittest.TestCase):
    def test_blocks_mutating_oc(self):
        for args in [['delete','pod','x'], ['patch','deployment','x'], ['adm','drain','node-a']]:
            with self.assertRaises(CommandBlocked): validate_oc_args(args)
    def test_blocks_secret_content(self):
        with self.assertRaises(CommandBlocked): validate_oc_args(['get','secrets'])
        with self.assertRaises(CommandBlocked): validate_oc_args(['get','secret/foo'])
        with self.assertRaises(CommandBlocked): validate_oc_args(['get','pods,secrets'])
    def test_allows_readonly(self):
        validate_oc_args(['get','pods','-A','-o','wide']); validate_oc_args(['auth','can-i','--list'])
    def test_subprocess_uses_argument_list(self):
        completed=subprocess.CompletedProcess(['oc','version'],0,'ok','')
        with patch('subprocess.run', return_value=completed) as mocked:
            result=run_oc(['version'])
        self.assertIsInstance(mocked.call_args.args[0], list)
        self.assertIsNot(mocked.call_args.kwargs.get('shell'), True)
        self.assertEqual(result.exit_code, 0)
    def test_allows_only_known_command_prefix(self):
        with patch.dict('os.environ', {'OPENSHIFT_AIOPS_COMMAND_PREFIX': 'flatpak-spawn --host', 'OPENSHIFT_AIOPS_OC_BIN': '/tmp/oc'}):
            self.assertEqual(command_prefix(), ['flatpak-spawn', '--host'])
            self.assertEqual(build_oc_command(['version'])[:3], ['flatpak-spawn', '--host', '/tmp/oc'])
        with patch.dict('os.environ', {'OPENSHIFT_AIOPS_COMMAND_PREFIX': 'sh -c'}):
            with self.assertRaises(CommandBlocked):
                command_prefix()
    def test_preflight_offline_does_not_call_oc(self):
        args=argparse.Namespace(offline=True, timeout=10)
        with patch('mcp_server.commands.run_oc') as mocked, redirect_stdout(io.StringIO()):
            code=preflight(args)
        mocked.assert_not_called()
        self.assertIn(code, {0, 2})
    def test_production_requires_confirmation(self):
        args=argparse.Namespace(environment='production', cluster='cluster-prd', context=None, confirm_production=None, timeout=10, offline=True)
        with patch.dict('os.environ', {}, clear=True), patch('sys.stdin', io.StringIO()):
            with self.assertRaises(ValidationError):
                require_production_confirmation(args)
        args.confirm_production='cluster-prd'
        with patch.dict('os.environ', {}, clear=True):
            require_production_confirmation(args)
if __name__ == '__main__': unittest.main()
