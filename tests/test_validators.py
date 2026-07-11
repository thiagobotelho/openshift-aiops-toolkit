import unittest
from mcp_server.validators import ValidationError, validate_k8s_name, validate_namespace, validate_tail, validate_timeout, validate_workload_kind
class ValidatorTests(unittest.TestCase):
    def test_valid_names(self):
        self.assertEqual(validate_k8s_name('app-1'), 'app-1')
        self.assertEqual(validate_namespace('openshift-monitoring'), 'openshift-monitoring')
    def test_blocks_dangerous_chars(self):
        for value in ['bad;name', 'bad|name', 'bad$(x)', 'bad`x`', '../bad']:
            with self.assertRaises(ValidationError): validate_k8s_name(value)
    def test_limits(self):
        self.assertEqual(validate_tail('10'), 10)
        with self.assertRaises(ValidationError): validate_tail('999999')
        self.assertEqual(validate_timeout('30'), 30)
        with self.assertRaises(ValidationError): validate_timeout('9999')
    def test_workload_kind(self):
        self.assertEqual(validate_workload_kind('Deployment'), 'deployment')
        with self.assertRaises(ValidationError): validate_workload_kind('pod')
if __name__ == '__main__': unittest.main()
