#!/usr/bin/env python3
import click
import os
import json
from pathlib import Path
from parser import NoteParser
from exporter import DataExporter

@click.command()
@click.option('--file', '-f', help='Note file to parse')
@click.option('--format', '-t', default='auto', help='Input format (markdown, txt, auto)')
@click.option('--output', '-o', help='Output file path')
@click.option('--summary', '-s', is_flag=True, help='Generate summary')
def parse_notes(file, format, output, summary):
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
        
        # Convert sets to lists for JSON serialization
        if 'tags' in result:
            result['tags'] = list(result['tags'])
        if 'keywords' in result:
            result['keywords'] = list(result['keywords'])
        
        # Display results
        click.echo(f"\nFormat: {result['format']}")
        if result.get('headers'):
            click.echo(f"Headers found: {len(result['headers'])}")
        if result.get('tags'):
            click.echo(f"Tags: {', '.join(result['tags'])}")
        if result.get('keywords'):
            click.echo(f"Keywords: {', '.join(result['keywords'])}")
        if result.get('todos'):
            click.echo(f"TODOs: {len(result['todos'])}")
        
        # Generate summary if requested
        if summary:
            try:
                click.echo("\n--- SUMMARY ---")
                summary_text = parser.generate_summary(result)
                click.echo(summary_text)
            except Exception as e:
                click.echo(f"Warning: Could not generate summary: {e}")
        
        # Save to output file if specified
        if output:
            try:
                exporter = DataExporter()
                output_path = Path(output)
                
                # Create output directory if it doesn't exist
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                if output_path.suffix.lower() == '.csv':
                    exporter.export_to_csv(result, output)
                    click.echo(f"Results exported to CSV: {output}")
                else:
                    exporter.export_to_json(result, output)
                    click.echo(f"Results saved as JSON: {output}")
            except PermissionError:
                click.echo(f"Error: Permission denied writing to {output}")
            except Exception as e:
                click.echo(f"Error saving output file: {e}")
            
    except FileNotFoundError as e:
        click.echo(f"Error: {e}")
    except PermissionError as e:
        click.echo(f"Error: {e}")
    except ValueError as e:
        click.echo(f"Error: {e}")
    except Exception as e:
        click.echo(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
if __name__ == '__main__':
    parse_notes()