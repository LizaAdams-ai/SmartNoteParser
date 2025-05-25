#!/usr/bin/env python3
import click
import os
import json
from pathlib import Path
from typing import Dict, List
from parser import NoteParser
from exporter import DataExporter
from config import Config
from watcher import FileWatcher

@click.command()
@click.option('--file', '-f', help='Note file to parse')
@click.option('--directory', '-d', help='Directory to process (batch mode)')
@click.option('--format', '-t', default='auto', help='Input format (markdown, txt, auto)')
@click.option('--output', '-o', help='Output file path')
@click.option('--summary', '-s', is_flag=True, help='Generate summary')
@click.option('--analyze', '-a', is_flag=True, help='Perform advanced text analysis')
@click.option('--config', '-c', help='Configuration file path')
@click.option('--recursive', '-r', is_flag=True, help='Process subdirectories recursively')
@click.option('--watch', '-w', is_flag=True, help='Watch files for changes and reprocess')
def parse_notes(file, directory, format, output, summary, analyze, config, recursive, watch):
    """SmartNoteParser - Extract key information from notes"""
    
    # Load configuration
    cfg = Config(config) if config else Config()
    
    # Determine input mode
    if directory:
        # Batch processing mode
        files_to_process = get_files_from_directory(directory, recursive)
        if not files_to_process:
            click.echo(f"No note files found in {directory}")
            return
        
        click.echo(f"Found {len(files_to_process)} files to process")
        results = []
        
        for file_path in files_to_process:
            click.echo(f"Processing {file_path}...")
            try:
                result = process_single_file(file_path, cfg, summary, analyze)
                result['source_file'] = str(file_path)
                results.append(result)
            except Exception as e:
                click.echo(f"Error processing {file_path}: {e}")
                continue
        
        # Export batch results
        if output:
            export_batch_results(results, output)
        else:
            display_batch_summary(results)
            
    elif file:
        # Single file mode
        if not os.path.exists(file):
            click.echo(f"File {file} not found")
            return
        
        click.echo(f"Parsing {file}...")
        try:
            result = process_single_file(file, cfg, summary, analyze)
            
            if output:
                export_single_result(result, output)
            else:
                display_single_result(result, summary, analyze, cfg)
                
        except Exception as e:
            handle_error(e)
    else:
        click.echo("Please specify either --file or --directory")
        return
    
    # Watch mode
    if watch:
        def watch_callback(file_path: str):
            """Callback for file changes"""
            try:
                click.echo(f"Processing changed file: {file_path}")
                result = process_single_file(file_path, cfg, summary, analyze)
                display_single_result(result, summary, analyze, cfg)
            except Exception as e:
                click.echo(f"Error processing {file_path}: {e}")
        
        watcher = FileWatcher(watch_callback)
        
        if file:
            watcher.watch_file(file)
        elif directory:
            watcher.watch_directory(directory, recursive)
        
        watcher.start()

def get_files_from_directory(directory: str, recursive: bool) -> List[Path]:
    """Get all note files from directory"""
    dir_path = Path(directory)
    extensions = ['*.md', '*.markdown', '*.txt']
    files = []
    
    for ext in extensions:
        if recursive:
            pattern = f"**/{ext}"
            files.extend(dir_path.glob(pattern))
        else:
            files.extend(dir_path.glob(ext))
    
    return sorted(files)

def process_single_file(file_path: str, cfg: Config, show_summary: bool, do_analysis: bool = False) -> Dict:
    """Process a single file and return results"""
    parser = NoteParser(cfg)
    result = parser.parse_file(file_path)
    
    # Convert sets to lists for JSON serialization
    if 'tags' in result:
        result['tags'] = list(result['tags'])
    if 'keywords' in result:
        result['keywords'] = list(result['keywords'])
    
    # Add analysis if requested
    if do_analysis:
        result = parser.analyze_content(result)
    
    if show_summary:
        result['summary'] = parser.generate_summary(result)
    
    return result

def display_single_result(result: Dict, show_summary: bool, do_analysis: bool, cfg: Config):
    """Display results for single file"""
    click.echo(f"\nFormat: {result['format']}")
    if result.get('headers'):
        click.echo(f"Headers found: {len(result['headers'])}")
    if result.get('tags'):
        max_tags = cfg.get('summary.max_tags_shown', 10)
        tags_to_show = result['tags'][:max_tags]
        click.echo(f"Tags: {', '.join(tags_to_show)}")
    if result.get('keywords'):
        max_keywords = cfg.get('summary.max_keywords_shown', 8)
        keywords_to_show = result['keywords'][:max_keywords]
        click.echo(f"Keywords: {', '.join(keywords_to_show)}")
    if result.get('todos'):
        click.echo(f"TODOs: {len(result['todos'])}")
    
    if show_summary and 'summary' in result:
        click.echo("\n--- SUMMARY ---")
        click.echo(result['summary'])
    
    # Display analysis results
    if do_analysis and 'analysis' in result:
        click.echo("\n--- ANALYSIS ---")
        analysis = result['analysis']
        
        # Top words
        if 'top_words' in analysis:
            top_words = analysis['top_words'][:5]
            words_str = ', '.join([f"{word}({count})" for word, count in top_words])
            click.echo(f"Top words: {words_str}")
        
        # Readability
        if 'readability' in analysis:
            read = analysis['readability']
            click.echo(f"Readability: {read.get('flesch_reading_ease', 0)} (Flesch score)")
            click.echo(f"Avg words/sentence: {read.get('avg_words_per_sentence', 0)}")
        
        # Sentiment indicators
        if 'sentiment_indicators' in analysis:
            sent = analysis['sentiment_indicators']
            click.echo(f"Sentiment indicators - Positive: {sent.get('positive_indicators', 0)}, "
                      f"Negative: {sent.get('negative_indicators', 0)}, "
                      f"Urgent: {sent.get('urgent_indicators', 0)}")

def display_batch_summary(results: List[Dict]):
    """Display summary for batch processing"""
    total_files = len(results)
    total_tags = sum(len(r.get('tags', [])) for r in results)
    total_todos = sum(len(r.get('todos', [])) for r in results)
    formats = [r.get('format') for r in results]
    
    click.echo(f"\n=== BATCH SUMMARY ===")
    click.echo(f"Files processed: {total_files}")
    click.echo(f"Total tags found: {total_tags}")
    click.echo(f"Total TODOs found: {total_todos}")
    click.echo(f"Formats: {', '.join(set(formats))}")

def export_single_result(result: Dict, output: str):
    """Export single file result"""
    try:
        exporter = DataExporter()
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if output_path.suffix.lower() == '.csv':
            exporter.export_to_csv(result, output)
            click.echo(f"Results exported to CSV: {output}")
        else:
            exporter.export_to_json(result, output)
            click.echo(f"Results saved as JSON: {output}")
    except Exception as e:
        click.echo(f"Error saving output: {e}")

def export_batch_results(results: List[Dict], output: str):
    """Export batch processing results"""
    try:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if output_path.suffix.lower() == '.csv':
            # Combine all results into one CSV
            combined_data = []
            for result in results:
                # Flatten result for CSV
                for item_type, items in [('tag', result.get('tags', [])), 
                                       ('keyword', result.get('keywords', [])),
                                       ('todo', result.get('todos', [])),
                                       ('header', [h[1] for h in result.get('headers', [])])]:
                    for item in items:
                        combined_data.append({
                            'source_file': result.get('source_file', ''),
                            'format': result.get('format', ''),
                            'type': item_type,
                            'content': item
                        })
            
            import pandas as pd
            df = pd.DataFrame(combined_data)
            df.to_csv(output, index=False)
            click.echo(f"Batch results exported to CSV: {output}")
        else:
            # JSON format - save all results
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            click.echo(f"Batch results saved as JSON: {output}")
            
    except Exception as e:
        click.echo(f"Error saving batch results: {e}")

def handle_error(e: Exception):
    """Handle different types of errors"""
    if isinstance(e, FileNotFoundError):
        click.echo(f"Error: {e}")
    elif isinstance(e, PermissionError):
        click.echo(f"Error: {e}")
    elif isinstance(e, ValueError):
        click.echo(f"Error: {e}")
    else:
        click.echo(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        
if __name__ == '__main__':
    parse_notes()