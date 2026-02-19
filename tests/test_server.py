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
    def _post_phone(self, payload):
        conn = http.client.HTTPConnection(self.addr, self.port, timeout=5)
        body = json.dumps(payload).encode("utf-8")
        conn.request("POST", "/api/phone-interest", body, {"Content-Type": "application/json"})
        return conn.getresponse()
    def _get(self, path):
        conn = http.client.HTTPConnection(self.addr, self.port, timeout=5)
        conn.request("GET", path)
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
    def test_reviews_api_returns_data(self):
        path = os.path.join(server.ROOT_DIR, "reviews.json")
        data = [
            {"name": "A", "rating": 5, "text": "t", "date": "d", "source": "Avito"},
            {"name": "B", "rating": 4, "text": "t2", "date": "d2", "source": "Avito"}
        ]
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            resp = self._get("/api/reviews")
            body = resp.read()
            self.assertEqual(resp.status, 200)
            obj = json.loads(body.decode("utf-8"))
            self.assertEqual(obj, data)
        finally:
            if os.path.exists(path):
                os.remove(path)
    def test_reviews_api_empty_when_missing(self):
        path = os.path.join(server.ROOT_DIR, "reviews.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write("[]")
        if os.path.exists(path):
            os.remove(path)
        resp = self._get("/api/reviews")
        body = resp.read()
        self.assertEqual(resp.status, 200)
        obj = json.loads(body.decode("utf-8"))
        self.assertEqual(obj, [])
    def test_phone_interest_falls_back_to_local_store(self):
        server.BOT_TOKEN = None
        server.CHAT_ID = None
        path = os.path.join(server.ROOT_DIR, "requests.log")
        if os.path.exists(path):
            os.remove(path)
        resp = self._post_phone({"page": "http://example.com", "phone": "tel:+79990000000"})
        data = resp.read()
        self.assertEqual(resp.status, 200)
        obj = json.loads(data.decode("utf-8"))
        self.assertTrue(obj["ok"])
        self.assertIsNone(obj["error"])
        self.assertTrue(os.path.exists(path))
        if os.path.exists(path):
            os.remove(path)
    def test_phone_interest_send_returns_ok_true(self):
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
            resp = self._post_phone({"page": "http://example.com", "phone": "tel:+79990000000"})
            data = resp.read()
            self.assertEqual(resp.status, 200)
            obj = json.loads(data.decode("utf-8"))
            self.assertTrue(obj["ok"])
            self.assertIsNone(obj["error"])
    def test_phone_interest_send_with_cert_path_sets_info(self):
        server.BOT_TOKEN = "x"
        server.CHAT_ID = "123"
        server.CERT_PATH = "cert.pem"
        def fake_urlopen(req, timeout=10, context=None):
            class R:
                def __enter__(self):
                    return self
                def __exit__(self, exc_type, exc, tb):
                    return False
                def read(self):
                    return b'{"ok": true, "result": {}}'
            return R()
        with patch("server.ssl.create_default_context", lambda cafile=None: object()):
            with patch("server.urllib.request.urlopen", fake_urlopen):
                resp = self._post_phone({"page": "http://example.com", "phone": "tel:+79990000000"})
                data = resp.read()
                self.assertEqual(resp.status, 200)
                obj = json.loads(data.decode("utf-8"))
                self.assertTrue(obj["ok"])
        server.CERT_PATH = None
    def test_phone_interest_ssl_error_uses_unverified_context(self):
        server.BOT_TOKEN = "x"
        server.CHAT_ID = "123"
        calls = {"count": 0}
        def fake_urlopen(req, timeout=10, context=None):
            if calls["count"] == 0:
                calls["count"] += 1
                raise server.ssl.SSLError("fail")
            class R:
                def __enter__(self):
                    return self
                def __exit__(self, exc_type, exc, tb):
                    return False
                def read(self):
                    return b'{"ok": true, "result": {}}'
            return R()
        with patch("server.urllib.request.urlopen", fake_urlopen):
            resp = self._post_phone({"page": "http://example.com", "phone": "tel:+79990000000"})
            data = resp.read()
            self.assertEqual(resp.status, 200)
            obj = json.loads(data.decode("utf-8"))
            self.assertTrue(obj["ok"])
    def test_phone_interest_send_error_response(self):
        server.BOT_TOKEN = "x"
        server.CHAT_ID = "123"
        def fake_urlopen(req, timeout=10, context=None):
            class R:
                def __enter__(self):
                    return self
                def __exit__(self, exc_type, exc, tb):
                    return False
                def read(self):
                    return b'{"ok": false, "description": "fail"}'
            return R()
        with patch("server.urllib.request.urlopen", fake_urlopen):
            resp = self._post_phone({"page": "http://example.com", "phone": "tel:+79990000000"})
            data = resp.read()
            self.assertEqual(resp.status, 200)
            obj = json.loads(data.decode("utf-8"))
            self.assertFalse(obj["ok"])
    def test_phone_interest_send_exception_sets_error(self):
        server.BOT_TOKEN = "x"
        server.CHAT_ID = "123"
        def fake_urlopen(req, timeout=10, context=None):
            raise RuntimeError("boom")
        with patch("server.urllib.request.urlopen", fake_urlopen):
            resp = self._post_phone({"page": "http://example.com", "phone": "tel:+79990000000"})
            data = resp.read()
            self.assertEqual(resp.status, 200)
            obj = json.loads(data.decode("utf-8"))
            self.assertFalse(obj["ok"])
    def test_phone_interest_log_write_error(self):
        server.BOT_TOKEN = None
        server.CHAT_ID = None
        with patch("builtins.open", side_effect=OSError("nope")):
            resp = self._post_phone({"page": "http://example.com", "phone": "tel:+79990000000"})
            data = resp.read()
            self.assertEqual(resp.status, 200)
            obj = json.loads(data.decode("utf-8"))
            self.assertFalse(obj["ok"])
    def test_static_get_root(self):
        resp = self._get("/")
        resp.read()
        self.assertEqual(resp.status, 200)
