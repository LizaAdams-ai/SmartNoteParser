import re
from typing import Dict, List, Set
from pathlib import Path

class NoteParser:
    def __init__(self):
        self.tags = set()
        self.todos = []
        self.headers = []
        self.content = ""
    
    def parse_file(self, file_path: str) -> Dict:
        """Parse a note file and extract structured information"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.content = content
        
        # Detect file type
        file_type = self._detect_format(path.suffix)
        
        if file_type == 'markdown':
            return self._parse_markdown(content)
        else:
            return self._parse_text(content)
    
    def _detect_format(self, extension: str) -> str:
        """Detect note format based on extension"""
        if extension.lower() in ['.md', '.markdown']:
            return 'markdown'
        return 'text'
    
    def _parse_markdown(self, content: str) -> Dict:
        """Parse markdown content"""
        result = {
            'format': 'markdown',
            'headers': [],
            'tags': set(),
            'todos': [],
            'content': content
        }
        
        # Extract headers
        headers = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        result['headers'] = [(len(h[0]), h[1].strip()) for h in headers]
        
        # Extract tags (hashtags)
        tags = re.findall(r'#(\w+)', content)
        result['tags'] = set(tags)
        
        # Extract todos
        todos = re.findall(r'- \[ \] (.+)', content)
        result['todos'] = todos
        
        return result
    
    def _parse_text(self, content: str) -> Dict:
        """Parse plain text content"""
        result = {
            'format': 'text', 
            'tags': set(),
            'todos': [],
            'content': content
        }
        
        # Extract simple patterns
        tags = re.findall(r'#(\w+)', content)
        result['tags'] = set(tags)
        
        # Look for TODO patterns
        todos = re.findall(r'TODO:?\s*(.+)', content, re.IGNORECASE)
        result['todos'] = todos
        
        return result