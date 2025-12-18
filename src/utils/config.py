import os
from pathlib import Path
from dotenv import load_dotenv
import yaml

class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        project_root = Path(__file__).parent.parent.parent
        
        env_path = project_root / '.env'
        load_dotenv(env_path)
        
        config_dir = project_root / 'config'
        
        settings_path = config_dir / 'settings.yaml'
        if settings_path.exists():
            with open(settings_path, 'r') as f:
                self.settings = yaml.safe_load(f) or {}
        else:
            self.settings = {}
        
        schedules_path = config_dir / 'bot_config.yaml'
        if schedules_path.exists():
            with open(schedules_path, 'r') as f:
                self.bot_schedules = yaml.safe_load(f) or {}
        else:
            self.bot_schedules = {}
        
        self._initialized = True
    
    def get_env(self, key, default=None):
        return os.getenv(key, default)
    
    def get_required_env(self, key):
        value = os.getenv(key)
        if value is None:
            raise ValueError(
                f"Required environment variable '{key}' is not set. "
                f"Please add it to your .env file."
            )
        return value
    
    def get_bot_config(self, bot_name):
        bots = self.bot_schedules.get('bots', [])
        return next((b for b in bots if b['name'] == bot_name), None)
    
    def get_setting(self, key, default=None):
        keys = key.split('.')
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value

config = Config()
