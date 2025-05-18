import json
import csv
import pandas as pd
from typing import Dict, List
from pathlib import Path

class DataExporter:
    def __init__(self):
        pass
    
    def export_to_csv(self, parsed_data: Dict, output_path: str) -> None:
        """Export parsed data to CSV format"""
        rows = []
        
        # Basic info row
        basic_info = {
            'type': 'document_info',
            'format': parsed_data.get('format', ''),
            'content_words': len(parsed_data.get('content', '').split()),
            'content_lines': len(parsed_data.get('content', '').splitlines()),
            'header_count': len(parsed_data.get('headers', [])),
            'tag_count': len(parsed_data.get('tags', [])),
            'keyword_count': len(parsed_data.get('keywords', [])),
            'todo_count': len(parsed_data.get('todos', [])),
        }
        rows.append(basic_info)
        
        # Headers
        for level, title in parsed_data.get('headers', []):
            rows.append({
                'type': 'header',
                'level': level,
                'content': title,
                'format': parsed_data.get('format', ''),
                'content_words': '',
                'content_lines': '',
                'header_count': '',
                'tag_count': '',
                'keyword_count': '',
                'todo_count': '',
            })
        
        # Tags
        for tag in parsed_data.get('tags', []):
            rows.append({
                'type': 'tag',
                'content': tag,
                'level': '',
                'format': parsed_data.get('format', ''),
                'content_words': '',
                'content_lines': '',
                'header_count': '',
                'tag_count': '',
                'keyword_count': '',
                'todo_count': '',
            })
        
        # Keywords
        for keyword in parsed_data.get('keywords', []):
            rows.append({
                'type': 'keyword', 
                'content': keyword,
                'level': '',
                'format': parsed_data.get('format', ''),
                'content_words': '',
                'content_lines': '',
                'header_count': '',
                'tag_count': '',
                'keyword_count': '',
                'todo_count': '',
            })
        
        # TODOs
        for todo in parsed_data.get('todos', []):
            rows.append({
                'type': 'todo',
                'content': todo,
                'level': '',
                'format': parsed_data.get('format', ''),
                'content_words': '',
                'content_lines': '',
                'header_count': '',
                'tag_count': '',
                'keyword_count': '',
                'todo_count': '',
            })
        
        # Write to CSV
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)
    
    def export_to_json(self, parsed_data: Dict, output_path: str) -> None:
        """Export parsed data to JSON format"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, indent=2, ensure_ascii=False)