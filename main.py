import sys
import yaml
from pathlib import Path
from src.core.messenger import Messenger
from src.bots.binformation_bot import BinformationBot

BOT_REGISTRY = {
    "BinformationBot": BinformationBot,
}

def run_bot(bot_name):
    config_path = Path(__file__).parent / 'config' / 'bot_config.yaml'

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    bot_config = next((b for b in config['bots'] if b['name'] == bot_name), None)
    if not bot_config:
        print(f"Error: Bot '{bot_name}' not found")
        sys.exit(1)

    messenger = Messenger(bot_name=bot_name)

    bot_class = BOT_REGISTRY[bot_config['type']]
    bot_kwargs = {k: v for k, v in bot_config.items()
                  if k not in ['name', 'type']}

    bot = bot_class(bot_name, messenger, bot_kwargs)
    bot.run()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <bot_name>")
        sys.exit(1)

    run_bot(sys.argv[1])
