import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import click

class NoteFileHandler(FileSystemEventHandler):
    """Handle file system events for note files"""
    
    def __init__(self, callback_func, extensions=None):
        self.callback_func = callback_func
        self.extensions = extensions or ['.md', '.markdown', '.txt']
        self.last_processed = {}
        
    def on_modified(self, event):
        if not event.is_directory:
            self._handle_file_change(event.src_path)
    
    def on_created(self, event):
        if not event.is_directory:
            self._handle_file_change(event.src_path)
    
    def _handle_file_change(self, file_path):
        """Handle changes to note files"""
        path = Path(file_path)
        
        # Check if file has relevant extension
        if path.suffix.lower() not in self.extensions:
            return
        
        # Debounce - avoid processing same file too frequently
        now = time.time()
        if file_path in self.last_processed:
            if now - self.last_processed[file_path] < 2.0:  # 2 second debounce
                return
        
        self.last_processed[file_path] = now
        
        click.echo(f"\nFile changed: {file_path}")
        self.callback_func(file_path)

class FileWatcher:
    """Watch files and directories for changes"""
    
    def __init__(self, callback_func):
        self.callback_func = callback_func
        self.observer = Observer()
        
    def watch_file(self, file_path: str):
        """Watch a single file"""
        file_path = Path(file_path)
        directory = file_path.parent
        
        handler = NoteFileHandler(
            lambda path: self.callback_func(path) if Path(path).name == file_path.name else None
        )
        
        self.observer.schedule(handler, str(directory), recursive=False)
        
    def watch_directory(self, directory: str, recursive: bool = False):
        """Watch a directory for changes"""
        handler = NoteFileHandler(self.callback_func)
        self.observer.schedule(handler, directory, recursive=recursive)
        
    def start(self):
        """Start watching"""
        click.echo("Starting file watcher... (Press Ctrl+C to stop)")
        self.observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            click.echo("\nStopping file watcher...")
            self.observer.stop()
        
        self.observer.join()