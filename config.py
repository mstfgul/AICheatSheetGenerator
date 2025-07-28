import os
from pathlib import Path
from typing import Dict, Any, Optional
import json

class Config:
    def __init__(self):
        self.config_dir = Path.home() / ".cheat_sheet_agent"
        self.config_file = self.config_dir / "config.json"
        self.ensure_config_dir()
        self.load_config()
    
    def ensure_config_dir(self):
        self.config_dir.mkdir(exist_ok=True)
    
    def load_config(self):
        self.default_config = {
            "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
            "default_difficulty": "intermediate",
            "default_format": "comprehensive",
            "default_include_examples": True,
            "output_directory": "cheat_sheets",
            "model": "gpt-4o",
            "max_tokens": 16000,
            "temperature": 0.7
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                    self.default_config.update(saved_config)
            except (json.JSONDecodeError, IOError):
                pass
    
    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.default_config, f, indent=2)
        except IOError:
            pass
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.default_config.get(key, default)
    
    def set(self, key: str, value: Any):
        self.default_config[key] = value
        self.save_config()
    
    def get_api_key(self) -> Optional[str]:
        api_key = self.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
        return api_key if api_key else None