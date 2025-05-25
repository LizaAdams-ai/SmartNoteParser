import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional

class Config:
    """Configuration manager for SmartNoteParser"""
    
    DEFAULT_CONFIG = {
        "parsing": {
            "ignore_case": True,
            "max_tag_length": 50,
            "custom_tag_patterns": [],
            "custom_todo_patterns": ["TODO:", "FIXME:", "NOTE:"],
            "extract_urls": True,
            "extract_emails": False
        },
        "export": {
            "default_format": "json",
            "csv_delimiter": ",",
            "include_content": False,
            "max_content_preview": 100
        },
        "summary": {
            "max_tags_shown": 10,
            "max_keywords_shown": 8,
            "include_word_count": True,
            "include_structure": True
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self.DEFAULT_CONFIG.copy()
        self.config_path = config_path or self._find_config_file()
        
        if self.config_path and Path(self.config_path).exists():
            self.load_config()
    
    def _find_config_file(self) -> Optional[str]:
        """Find config file in common locations"""
        possible_paths = [
            ".smartnoteparser.json",
            ".smartnoteparser.yaml",
            "config.json",
            "config.yaml",
            Path.home() / ".smartnoteparser.json"
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return str(path)
        return None
    
    def load_config(self):
        """Load configuration from file"""
        try:
            path = Path(self.config_path)
            
            if path.suffix.lower() in ['.yaml', '.yml']:
                with open(path, 'r') as f:
                    loaded_config = yaml.safe_load(f)
            else:
                with open(path, 'r') as f:
                    loaded_config = json.load(f)
            
            # Merge with defaults
            self._merge_config(loaded_config)
            
        except Exception as e:
            print(f"Warning: Could not load config from {self.config_path}: {e}")
    
    def _merge_config(self, loaded_config: Dict):
        """Recursively merge loaded config with defaults"""
        def merge_dict(default, loaded):
            for key, value in loaded.items():
                if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                    merge_dict(default[key], value)
                else:
                    default[key] = value
        
        merge_dict(self.config, loaded_config)
    
    def get(self, key_path: str, default=None):
        """Get config value using dot notation (e.g., 'parsing.ignore_case')"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def save_default_config(self, path: str):
        """Save default config to file"""
        with open(path, 'w') as f:
            json.dump(self.DEFAULT_CONFIG, f, indent=2)
    
    def get_custom_patterns(self) -> Dict[str, List[str]]:
        """Get custom regex patterns"""
        return {
            'tags': self.get('parsing.custom_tag_patterns', []),
            'todos': self.get('parsing.custom_todo_patterns', [])
        }