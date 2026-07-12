import unittest
from mcp_server.sanitizers import REDACTION, sanitize_obj, sanitize_text
class SanitizerTests(unittest.TestCase):
    def test_redacts_tokens_and_passwords(self):
        text='Authorization: Bearer abcdefghijklmnop password=supersecret access_token=tokenvalue'
        out=sanitize_text(text)
        self.assertIn(REDACTION, out); self.assertNotIn('supersecret', out); self.assertNotIn('abcdefghijklmnop', out)
    def test_redacts_url_credentials(self):
        out=sanitize_text('https://user:pass@example.com/path')
        self.assertIn(REDACTION, out); self.assertNotIn('user:pass', out)
    def test_redacts_refresh_token_jwt_and_base64(self):
        jwt='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.signaturepart'
        base64_value='A' * 100
        out=sanitize_text(f'refresh_token=refresh-secret {jwt} data={base64_value}')
        self.assertIn(REDACTION, out)
        self.assertNotIn('refresh-secret', out)
        self.assertNotIn(jwt, out)
        self.assertNotIn(base64_value, out)
    def test_redacts_object_keys(self):
        out=sanitize_obj({'client_secret':'abc','name':'pod-a'})
        self.assertEqual(out['client_secret'], REDACTION); self.assertEqual(out['name'], 'pod-a')
if __name__ == '__main__': unittest.main()
