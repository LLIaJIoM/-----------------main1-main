import threading
import time
import json
import http.client
import unittest
import os
from unittest.mock import patch
from http.server import HTTPServer
import server

class ServerTestCase(unittest.TestCase):
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

    def test_missing_fields_returns_400(self):
        server.BOT_TOKEN = None
        server.CHAT_ID = None
        resp = self._post({"name": "", "phone": ""})
        data = resp.read()
        self.assertEqual(resp.status, 400)
        obj = json.loads(data.decode("utf-8"))
        self.assertFalse(obj["ok"])
        self.assertEqual(obj["error"], "missing_fields")

    def test_env_missing_falls_back_to_local_store(self):
        server.BOT_TOKEN = None
        server.CHAT_ID = None
        resp = self._post({"name": "Alice", "phone": "+79990000000"})
        data = resp.read()
        self.assertEqual(resp.status, 200)
        obj = json.loads(data.decode("utf-8"))
        self.assertTrue(obj["ok"])
        self.assertIsNone(obj["error"])
        self.assertIn("info", obj)

    def test_successful_send_returns_ok_true(self):
        server.BOT_TOKEN = "x"
        server.CHAT_ID = "123"
        def fake_urlopen(req, timeout=10, context=None):
            class R:
                def __enter__(self):
                    return self
                def __exit__(self, exc_type, exc, tb):
                    return False
                def read(self):
                    return b'{"ok": true, "result": {}}'
            return R()
        with patch("server.urllib.request.urlopen", fake_urlopen):
            resp = self._post({"name": "Bob", "phone": "+79990000001", "comment": "c", "page": "/p"})
            data = resp.read()
            self.assertEqual(resp.status, 200)
            obj = json.loads(data.decode("utf-8"))
            self.assertTrue(obj["ok"])
            self.assertIsNone(obj["error"])

    def test_invalid_phone_returns_400(self):
        server.BOT_TOKEN = None
        server.CHAT_ID = None
        resp = self._post({"name": "Bad", "phone": "123"})
        data = resp.read()
        self.assertEqual(resp.status, 400)
        obj = json.loads(data.decode("utf-8"))
        self.assertFalse(obj["ok"])
        self.assertEqual(obj["error"], "invalid_phone")

    def test_invalid_name_chars_returns_400(self):
        server.BOT_TOKEN = None
        server.CHAT_ID = None
        resp = self._post({"name": "Ivan123", "phone": "+79990000000"})
        data = resp.read()
        self.assertEqual(resp.status, 400)
        obj = json.loads(data.decode("utf-8"))
        self.assertFalse(obj["ok"])
        self.assertEqual(obj["error"], "invalid_name_chars")

    def test_valid_cyrillic_name_ok(self):
        server.BOT_TOKEN = None
        server.CHAT_ID = None
        resp = self._post({"name": "Мария-Анна", "phone": "+79990000000"})
        data = resp.read()
        self.assertEqual(resp.status, 200)
        obj = json.loads(data.decode("utf-8"))
        self.assertTrue(obj["ok"])

    def test_translate_path_returns_string(self):
        handler = server.Handler.__new__(server.Handler)
        handler.directory = os.getcwd()
        result = server.Handler.translate_path(handler, "/")
        self.assertTrue(isinstance(result, str))
        self.assertNotEqual(result, "")
