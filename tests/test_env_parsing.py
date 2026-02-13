import os
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

    def test_chat_ids_none(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            if "TELEGRAM_CHAT_IDS" in os.environ:
                del os.environ["TELEGRAM_CHAT_IDS"]
            import server
            importlib.reload(server)
            self.assertIsNone(server.CHAT_IDS)

if __name__ == "__main__":
    unittest.main()
