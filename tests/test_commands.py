import argparse, io, subprocess, unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from mcp_server.commands import CommandBlocked, build_oc_command, cluster_name_from_api_server, command_prefix, detect_cluster_name, preflight, run_oc, validate_oc_args
from mcp_server.models import CommandResult
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
    def test_detects_cluster_name_from_infrastructure_first(self):
        infrastructure = CommandResult(['oc','get','infrastructure','cluster','-o','json'], 0, '{"status":{"infrastructureName":"crc-tg922"}}\n', '', 0.01)
        with patch('mcp_server.commands.run_oc', return_value=infrastructure):
            self.assertEqual(detect_cluster_name(), 'crc-tg922')
    def test_detects_crc_cluster_name_from_api_server_fallback(self):
        infrastructure = CommandResult(['oc','get','infrastructure','cluster','-o','json'], 1, '', 'not found', 0.01)
        command_result = CommandResult(['oc','whoami','--show-server'], 0, 'https://api.crc.testing:6443\n', '', 0.01)
        with patch('mcp_server.commands.run_oc', side_effect=[infrastructure, command_result]):
            self.assertEqual(detect_cluster_name(), 'crc')
    def test_cluster_name_from_api_server_is_safe(self):
        self.assertEqual(cluster_name_from_api_server('https://api.crc.testing:6443'), 'crc')
        self.assertEqual(cluster_name_from_api_server('https://api.cluster-prd.example.com:6443'), 'cluster-prd')
        self.assertEqual(cluster_name_from_api_server(''), 'openshift-cluster')
    def test_codebase_does_not_use_forbidden_execution_apis(self):
        root = Path(__file__).resolve().parents[1]
        forbidden = ['shell=True', 'os.system', 'os.popen', 'eval(']
        checked = []
        for base in ['mcp_server', 'scripts']:
            for path in (root / base).rglob('*'):
                if path.is_file() and path.suffix in {'.py', '.sh'}:
                    checked.append(path)
                    text = path.read_text(encoding='utf-8', errors='ignore')
                    for token in forbidden:
                        self.assertNotIn(token, text, f'{token} encontrado em {path}')
        text = (root / 'openshift-aiops').read_text(encoding='utf-8', errors='ignore')
        for token in forbidden:
            self.assertNotIn(token, text, f'{token} encontrado em openshift-aiops')
        self.assertTrue(checked)
if __name__ == '__main__': unittest.main()
