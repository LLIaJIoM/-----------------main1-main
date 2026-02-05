import threading
import time
import json
import http.client
import unittest
from unittest.mock import patch
from http.server import HTTPServer
import urllib.parse
import server

class MultiChatIdsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.CERT_PATH = None
        server.certifi = None
        cls.httpd = HTTPServer(("127.0.0.1", 0), server.Handler)
        cls.addr, cls.port = cls.httpd.server_address
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.05)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=1.0)

    def _post(self, payload):
        conn = http.client.HTTPConnection(self.addr, self.port, timeout=5)
        body = json.dumps(payload).encode("utf-8")
        conn.request("POST", "/api/telegram", body, {"Content-Type": "application/json"})
        return conn.getresponse()

    def test_send_to_multiple_chat_ids(self):
        server.BOT_TOKEN = "x"
        server.CHAT_ID = None
        server.CHAT_IDS = ["111", "222", "111"]
        captured = []
        def fake_urlopen(req, timeout=10, context=None):
            data = req.data or b""
            qs = urllib.parse.parse_qs(data.decode("utf-8"))
            captured.append((qs.get("chat_id") or [""])[0])
            class R:
                def __enter__(self): return self
                def __exit__(self, a,b,c): return False
                def read(self): return b'{"ok": true, "result": {}}'
            return R()
        with patch("server.urllib.request.urlopen", fake_urlopen):
            resp = self._post({"name": "Test", "phone": "+79990000000"})
            data = resp.read()
            self.assertEqual(resp.status, 200)
            obj = json.loads(data.decode("utf-8"))
            self.assertTrue(obj["ok"])
            self.assertIn("info", obj)
        self.assertEqual(captured, ["111", "222"])
