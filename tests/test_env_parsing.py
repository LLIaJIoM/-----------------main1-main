import os
import sys
import types
import runpy
import unittest
import importlib
from unittest.mock import patch, mock_open

class EnvParsingTests(unittest.TestCase):
    def test_chat_ids_parsing_json(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            with patch.dict(os.environ, {"TELEGRAM_CHAT_IDS": '["123", "456"]'}):
                import server
                importlib.reload(server)
                self.assertEqual(server.CHAT_IDS, ["123", "456"])

    def test_chat_ids_parsing_comma(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            with patch.dict(os.environ, {"TELEGRAM_CHAT_IDS": "111, 222"}):
                import server
                importlib.reload(server)
                self.assertEqual(server.CHAT_IDS, ["111", "222"])

    def test_chat_ids_parsing_invalid_json_fallback(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            with patch.dict(os.environ, {"TELEGRAM_CHAT_IDS": "{invalid"}):
                import server
                importlib.reload(server)
                self.assertEqual(server.CHAT_IDS, ["{invalid"])

    def test_chat_ids_parsing_non_list_json_fallback(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            with patch.dict(os.environ, {"TELEGRAM_CHAT_IDS": '{"a": 1}'}):
                import server
                importlib.reload(server)
                self.assertEqual(server.CHAT_IDS, ['{"a": 1}'])

    def test_chat_ids_none(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            with patch.dict(os.environ, {"TELEGRAM_CHAT_IDS": "x"}):
                del os.environ["TELEGRAM_CHAT_IDS"]
                import server
                importlib.reload(server)
                self.assertIsNone(server.CHAT_IDS)

    def test_certifi_failure_sets_none(self):
        fake = types.SimpleNamespace(where=lambda: (_ for _ in ()).throw(RuntimeError("fail")))
        with patch.dict(sys.modules, {"certifi": fake}):
            with patch("builtins.open", side_effect=FileNotFoundError):
                import server
                importlib.reload(server)
                self.assertIsNone(server.CERT_PATH)
                self.assertIsNone(server.certifi)

    def test_config_json_parsing(self):
        cfg = '{"TELEGRAM_BOT_TOKEN": "bt", "TELEGRAM_CHAT_ID": "cid", "TELEGRAM_CHAT_IDS": ["1", "2"]}'
        with patch("builtins.open", mock_open(read_data=cfg)):
            with patch.dict(os.environ, {}, clear=True):
                import server
                importlib.reload(server)
                self.assertEqual(server.BOT_TOKEN, "bt")
                self.assertEqual(server.CHAT_ID, "cid")
                self.assertEqual(server.CHAT_IDS, ["1", "2"])

    def test_main_reads_env_and_runs(self):
        import http.server
        calls = {"serve": 0, "close": 0, "chdir": 0}
        class DummyServer:
            def __init__(self, addr, handler): pass
            def serve_forever(self):
                calls["serve"] += 1
                raise KeyboardInterrupt()
            def server_close(self):
                calls["close"] += 1
        def fake_chdir(_):
            calls["chdir"] += 1
        with patch.object(http.server, "HTTPServer", DummyServer):
            with patch.object(os, "chdir", fake_chdir):
                with patch.dict(os.environ, {"HOST": "127.0.0.1", "PORT": "8001"}):
                    runpy.run_module("server", run_name="__main__")
        self.assertEqual(calls["serve"], 1)
        self.assertEqual(calls["close"], 1)
        self.assertEqual(calls["chdir"], 1)
