import json
import unittest
from unittest.mock import patch
from http.server import HTTPServer
import server

class PhoneCountryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.CERT_PATH = None
        server.certifi = None
        cls.httpd = HTTPServer(("127.0.0.1", 0), server.Handler)
        cls.addr, cls.port = cls.httpd.server_address
        import threading, time
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.05)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=1.0)

    def _post_json(self, obj):
        import http.client
        conn = http.client.HTTPConnection(self.addr, self.port, timeout=5)
        body = json.dumps(obj).encode("utf-8")
        conn.request("POST", "/api/telegram", body, {"Content-Type": "application/json"})
        return conn.getresponse()

    def test_fallback_log_contains_country_fields(self):
        server.BOT_TOKEN = None
        server.CHAT_ID = None
        # Capture write to file
        import builtins
        written = {"line": None}
        def fake_open(*args, **kwargs):
            class F:
                def __enter__(self): return self
                def __exit__(self, a,b,c): return False
                def write(self, s):
                    written["line"] = s
            return F()
        with patch.object(builtins, "open", fake_open):
            resp = self._post_json({
                "name": "John",
                "phone": "+15551234567",
                "comment": "",
                "page": "/",
                "phone_country": "United States",
                "phone_iso2": "us",
                "phone_dial_code": "1"
            })
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertTrue(data["ok"])
            line = written["line"]
            self.assertIsNotNone(line)
            rec = json.loads(line)
            self.assertEqual(rec.get("phone_country"), "United States")
            self.assertEqual(rec.get("phone_iso2"), "us")
            self.assertEqual(rec.get("phone_dial_code"), "1")

