import json
import ssl
import http.client
import unittest
from unittest.mock import patch
from http.server import HTTPServer
import server

class ServerErrorTests(unittest.TestCase):
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

    def _post_raw(self, path, body, headers=None):
        conn = http.client.HTTPConnection(self.addr, self.port, timeout=5)
        conn.request("POST", path, body, headers or {})
        return conn.getresponse()

    def _post_json(self, obj):
        return self._post_raw("/api/telegram", json.dumps(obj).encode("utf-8"), {"Content-Type": "application/json"})

    def test_unknown_path_returns_404(self):
        r = self._post_json({"name": "A", "phone": "+79990000000"})
        self.assertEqual(r.status, 200)
        r2 = self._post_raw("/api/unknown", b"{}", {"Content-Type": "application/json"})
        self.assertEqual(r2.status, 404)
        data = json.loads(r2.read().decode("utf-8"))
        self.assertEqual(data.get("error"), "not_found")

    def test_invalid_json_body_is_handled(self):
        resp = self._post_raw("/api/telegram", b"{bad json", {"Content-Type": "application/json"})
        self.assertEqual(resp.status, 400)
        data = json.loads(resp.read().decode("utf-8"))
        self.assertEqual(data.get("error"), "missing_fields")

    def test_telegram_error_description_propagates(self):
        server.BOT_TOKEN = "x"
        server.CHAT_ID = "123"
        def fake_urlopen(req, timeout=10, context=None):
            class R:
                def __enter__(self): return self
                def __exit__(self, a,b,c): return False
                def read(self):
                    return b'{"ok": false, "description": "Bad Request: chat not found"}'
            return R()
        with patch("server.urllib.request.urlopen", fake_urlopen):
            resp = self._post_json({"name": "A", "phone": "+79990000000", "comment": "c"})
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertFalse(data["ok"])
            self.assertEqual(data["error"], "Bad Request: chat not found")

    def test_tls_fallback_on_ssl_error(self):
        server.BOT_TOKEN = "x"
        server.CHAT_ID = "123"
        calls = {"n": 0}
        def urlopen_swap(req, timeout=10, context=None):
            calls["n"] += 1
            if calls["n"] == 1:
                raise ssl.SSLError("tls")
            class R:
                def __enter__(self): return self
                def __exit__(self, a,b,c): return False
                def read(self): return b'{"ok": true}'
            return R()
        with patch("server.urllib.request.urlopen", urlopen_swap):
            resp = self._post_json({"name": "B", "phone": "+79990000001"})
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertTrue(data["ok"])

    def test_certifi_path_uses_custom_context(self):
        server.BOT_TOKEN = "x"
        server.CHAT_ID = "123"
        server.CERT_PATH = "x"
        def fake_ctx(cafile=None):
            return object()
        def fake_urlopen(req, timeout=10, context=None):
            class R:
                def __enter__(self): return self
                def __exit__(self, a,b,c): return False
                def read(self): return b'{"ok": true}'
            return R()
        with patch("server.ssl.create_default_context", fake_ctx):
            with patch("server.urllib.request.urlopen", fake_urlopen):
                resp = self._post_json({"name": "E", "phone": "+79990000005"})
                self.assertEqual(resp.status, 200)
                data = json.loads(resp.read().decode("utf-8"))
                self.assertTrue(data["ok"])
        server.CERT_PATH = None

    def test_run_handles_keyboard_interrupt(self):
        calls = {"serve": 0, "close": 0}
        class DummyServer:
            def __init__(self, addr, handler): pass
            def serve_forever(self):
                calls["serve"] += 1
                raise KeyboardInterrupt()
            def server_close(self):
                calls["close"] += 1
        with patch("server.HTTPServer", DummyServer):
            with patch("server.os.chdir", lambda _: None):
                server.run("127.0.0.1", 0)
        self.assertEqual(calls["serve"], 1)
        self.assertEqual(calls["close"], 1)

    def test_local_store_failure_returns_error(self):
        server.BOT_TOKEN = None
        server.CHAT_ID = None
        import builtins
        def bad_open(*args, **kwargs):
            raise OSError("disk full")
        with patch.object(builtins, "open", bad_open):
            resp = self._post_json({"name": "C", "phone": "+79990000002"})
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertFalse(data["ok"])
            self.assertEqual(data["error"], "disk full")

    def test_name_too_long_returns_400(self):
        server.BOT_TOKEN = None
        server.CHAT_ID = None
        long_name = "A" * 51
        resp = self._post_json({"name": long_name, "phone": "+79990000003"})
        self.assertEqual(resp.status, 400)
        data = json.loads(resp.read().decode("utf-8"))
        self.assertFalse(data["ok"])
        self.assertEqual(data["error"], "name_too_long")

    def test_comment_too_long_returns_400(self):
        server.BOT_TOKEN = None
        server.CHAT_ID = None
        long_comment = "B" * 1001
        resp = self._post_json({"name": "D", "phone": "+79990000004", "comment": long_comment})
        self.assertEqual(resp.status, 400)
        data = json.loads(resp.read().decode("utf-8"))
        self.assertFalse(data["ok"])
        self.assertEqual(data["error"], "comment_too_long")
