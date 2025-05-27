# SmartNoteParser

An intelligent CLI tool to parse notes and extract structured information with advanced analysis capabilities.

## Features

- **Multi-format parsing**: Markdown and text files
- **Smart extraction**: Headers, tags, keywords, @mentions, TODO items
- **Batch processing**: Process entire directories recursively
- **Advanced analysis**: Word frequency, readability metrics, sentiment indicators
- **Export options**: JSON and CSV formats
- **File watching**: Auto-reprocess files when they change
- **Configurable**: YAML/JSON configuration files
- **Summary generation**: Structured document summaries

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
# Parse single file
python main.py --file notes.md

# With summary
python main.py --file notes.md --summary

# With advanced analysis
python main.py --file notes.md --analyze
```

### Batch Processing
```bash
# Process directory
python main.py --directory ./notes --output results.json

# Recursive processing
python main.py --directory ./notes --recursive --output results.csv
```

### File Watching
```bash
# Watch single file
python main.py --file notes.md --watch

# Watch directory
python main.py --directory ./notes --watch --analyze
```

### Configuration
```bash
# Use custom config
python main.py --file notes.md --config my-config.yaml

# Generate example config
cp config.example.yaml .smartnoteparser.yaml
```

## Supported Formats

- Markdown (.md, .markdown)
- Plain text (.txt)

## Example Output

```
Parsing notes.md...

Format: markdown
Headers found: 3
Tags: project, important, development
Keywords: authentication, database
TODOs: 2

--- ANALYSIS ---
Top words: project(5), implementation(3), testing(2)
Readability: 65.2 (Flesch score)
Avg words/sentence: 12.4
Sentiment indicators - Positive: 3, Negative: 1, Urgent: 2
```

## Configuration

Create `.smartnoteparser.yaml` in your project or home directory:

```yaml
parsing:
  custom_todo_patterns:
    - "TODO:"
    - "FIXME:"
    - "NOTE:"
  extract_urls: true

analysis:
  word_frequency_top_n: 15
  include_stop_words: false

export:
  default_format: "json"
  include_content: false
```