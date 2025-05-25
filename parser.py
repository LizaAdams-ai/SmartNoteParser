import re
from typing import Dict, List, Set, Optional
from pathlib import Path
from collections import Counter
from config import Config
from analyzer import TextAnalyzer

class NoteParser:
    def __init__(self, config: Optional[Config] = None):
        self.tags = set()
        self.todos = []
        self.headers = []
        self.content = ""
        self.config = config or Config()
        self.analyzer = TextAnalyzer()
    
    def parse_file(self, file_path: str) -> Dict:
        """Parse a note file and extract structured information"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except Exception as e:
                raise ValueError(f"Unable to read file {file_path}: {e}")
        except PermissionError:
            raise PermissionError(f"Permission denied reading file: {file_path}")
        except Exception as e:
            raise IOError(f"Error reading file {file_path}: {e}")
        
        if not content.strip():
            raise ValueError(f"File is empty: {file_path}")
        
        self.content = content
        
        # Detect file type
        file_type = self._detect_format(path.suffix)
        
        try:
            if file_type == 'markdown':
                return self._parse_markdown(content)
            else:
                return self._parse_text(content)
        except Exception as e:
            raise RuntimeError(f"Error parsing content: {e}")
    
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
            'keywords': set(),
            'content': content
        }
        
        # Extract headers
        headers = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        result['headers'] = [(len(h[0]), h[1].strip()) for h in headers]
        
        # Extract hashtags (avoid markdown headers)
        tags = re.findall(r'(?<!^)(?<!^#)(?<!^##)(?<!^###)(?<!^####)(?<!^#####)(?<!^######)#(\w+)', content, re.MULTILINE)
        result['tags'] = set(tags)
        
        # Extract @mentions and keywords in brackets
        mentions = re.findall(r'@(\w+)', content)
        keywords_brackets = re.findall(r'\[([^\]]+)\]', content)
        result['keywords'] = set(mentions + keywords_brackets)
        
        # Extract todos (multiple formats)
        todos = []
        todos.extend(re.findall(r'- \[ \] (.+)', content))
        todos.extend(re.findall(r'- \[x\] (.+)', content))
        todos.extend(re.findall(r'\* \[ \] (.+)', content))
        todos.extend(re.findall(r'TODO:?\s*(.+)', content, re.IGNORECASE))
        result['todos'] = list(set(todos))
        
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
    
    def generate_summary(self, parsed_data: Dict) -> str:
        """Generate a text summary of the parsed note"""
        lines = []
        
        # File format
        lines.append(f"Document Type: {parsed_data['format'].upper()}")
        
        # Structure info
        if parsed_data.get('headers'):
            levels = [h[0] for h in parsed_data['headers']]
            level_counts = Counter(levels)
            structure = ", ".join([f"H{level}: {count}" for level, count in sorted(level_counts.items())])
            lines.append(f"Structure: {structure}")
        
        # Content stats
        content = parsed_data.get('content', '')
        lines.append(f"Content: {len(content.split())} words, {len(content.splitlines())} lines")
        
        # Tags and keywords
        if parsed_data.get('tags'):
            lines.append(f"Tags: {', '.join(list(parsed_data['tags'])[:5])}")
        if parsed_data.get('keywords'):
            lines.append(f"Keywords: {', '.join(list(parsed_data['keywords'])[:5])}")
        
        # Tasks
        if parsed_data.get('todos'):
            completed = len([t for t in parsed_data['todos'] if 'x' in str(t)])
            total = len(parsed_data['todos'])
            lines.append(f"Tasks: {completed}/{total} completed")
        
        return "\n".join(lines)
    
    def analyze_content(self, parsed_data: Dict) -> Dict:
        """Perform advanced text analysis on parsed content"""
        content = parsed_data.get('content', '')
        if not content:
            return {}
        
        analysis = self.analyzer.generate_text_insights(content)
        
        # Add analysis results to parsed data
        result = parsed_data.copy()
        result['analysis'] = analysis
        
        return result