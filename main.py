#!/usr/bin/env python3
import click
import os
import json
from pathlib import Path
from parser import NoteParser

@click.command()
@click.option('--file', '-f', help='Note file to parse')
@click.option('--format', '-t', default='auto', help='Input format (markdown, txt, auto)')
@click.option('--output', '-o', help='Output file path')
def parse_notes(file, format, output):
    """SmartNoteParser - Extract key information from notes"""
    if not file:
        click.echo("Please specify a file to parse using --file")
        return
    
    if not os.path.exists(file):
        click.echo(f"File {file} not found")
        return
    
    click.echo(f"Parsing {file}...")
    
    try:
        parser = NoteParser()
        result = parser.parse_file(file)
        
        # Convert set to list for JSON serialization
        if 'tags' in result:
            result['tags'] = list(result['tags'])
        
        # Display results
        click.echo(f"\nFormat: {result['format']}")
        if result.get('headers'):
            click.echo(f"Headers found: {len(result['headers'])}")
        if result.get('tags'):
            click.echo(f"Tags: {', '.join(result['tags'])}")
        if result.get('todos'):
            click.echo(f"TODOs: {len(result['todos'])}")
        
        # Save to output file if specified
        if output:
            with open(output, 'w') as f:
                json.dump(result, f, indent=2)
            click.echo(f"Results saved to {output}")
            
    except Exception as e:
        click.echo(f"Error parsing file: {e}")
    
if __name__ == '__main__':
    parse_notes()