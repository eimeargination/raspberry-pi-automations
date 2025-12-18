import requests
import json
from datetime import datetime
from src.utils.config import config

class Messenger:

    def __init__(self, bot_name):
        self.bot_name = bot_name

        self._load_credentials(bot_name)

    def _load_credentials(self, bot_name):
        env_prefix = bot_name.upper().replace('-', '_')

        self.telegram_token = config.get_env(f'{env_prefix}_TELEGRAM_TOKEN')
        self.telegram_chat_id = config.get_env(f'{env_prefix}_TELEGRAM_CHAT_ID')


    def send(self, message, bot_name):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            return self._send_telegram(message)
        
        except Exception as e:
            print(f"[{timestamp}] Error sending message: {e}")
            return False

    def _send_telegram(self, message):
        if not self.telegram_token or not self.telegram_chat_id:
            raise ValueError(
                f"Telegram credentials not configured for bot '{self.bot_name}'. "
                f"Set {self.bot_name.upper()}_TELEGRAM_TOKEN and "
                f"{self.bot_name.upper()}_TELEGRAM_CHAT_ID in .env"
            )

        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            "chat_id": self.telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()

        result = response.json()
        if not result.get('ok'):
            raise Exception(f"Telegram API error: {result.get('description')}")

        print(f"✅ Sent to telegram")
