import json
import urllib.parse
import unittest
from unittest.mock import patch
from http.server import HTTPServer
import server

class MessageCountryTests(unittest.TestCase):
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

    def test_telegram_text_includes_country_line(self):
        server.BOT_TOKEN = "x"
        server.CHAT_ID = "123"
        captured = {"text": None}

        def fake_urlopen(req, timeout=10, context=None):
            data = req.data or b""
            qs = urllib.parse.parse_qs(data.decode("utf-8"))
            captured["text"] = (qs.get("text") or [""])[0]
            class R:
                def __enter__(self): return self
                def __exit__(self, a,b,c): return False
                def read(self): return b'{"ok": true, "result": {}}'
            return R()

        with patch("server.urllib.request.urlopen", fake_urlopen):
            resp = self._post_json({
                "name": "Иван",
                "phone": "+70000000000",
                "comment": "0",
                "page": "/",
                "phone_country": "Russia",
                "phone_iso2": "ru",
                "phone_dial_code": "7"
            })
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertTrue(data["ok"])

        text = captured["text"]
        self.assertIsNotNone(text)
        self.assertIn("Имя: Иван", text)
        self.assertIn("Телефон: +70000000000", text)
        self.assertIn("Страна: Россия", text)
        self.assertIn("Комментарий: 0", text)
        self.assertIn("Источник: Сайт", text)
