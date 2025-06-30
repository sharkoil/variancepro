"""
VariancePro Continuous Test Runner

This script watches for changes to Python files in the project and automatically runs
the relevant tests when files are modified. This supports test-driven development
by providing immediate feedback.

Usage:
    python continuous_test.py

Requirements:
    pip install watchdog pytest
"""

import sys
import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import datetime

class TestRunner(FileSystemEventHandler):
    """File system event handler for running tests on file changes"""
    
    def __init__(self, test_mapping=None):
        super().__init__()
        self.last_run_time = 0
        self.debounce_seconds = 2  # Prevent multiple runs within 2 seconds
        
        # Mapping of source files to test files
        # If a file is changed, run its corresponding test(s)
        self.test_mapping = test_mapping or {
            'app.py': ['test_timescale_analyzer_unit.py', 'test_timescale_analyzer_integration.py'],
            'utils/data_processor.py': ['test_timescale_analyzer_integration.py'],
            'test_timescale_analyzer_unit.py': ['test_timescale_analyzer_unit.py'],
            'test_timescale_analyzer_integration.py': ['test_timescale_analyzer_integration.py'],
            'test_financial_accuracy.py': ['test_financial_accuracy.py'],
            'test_timescale_analyzer_edge_cases.py': ['test_timescale_analyzer_edge_cases.py']
        }
    
    def on_modified(self, event):
        """Handle file modification event"""
        if not event.is_directory and event.src_path.endswith('.py'):
            current_time = time.time()
            
            # Debounce to prevent multiple runs for the same change
            if current_time - self.last_run_time < self.debounce_seconds:
                return
                
            self.last_run_time = current_time
            
            # Get the relative path of the changed file
            file_path = os.path.relpath(event.src_path, os.path.dirname(os.path.abspath(__file__)))
            file_path = file_path.replace('\\', '/')  # Normalize path separators
            
            # Run tests for the modified file
            self._run_tests_for_file(file_path)
    
    def _run_tests_for_file(self, file_path):
        """Run tests associated with a modified file"""
        print("\n" + "=" * 70)
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n🔄 File changed: {file_path} at {timestamp}")
        
        # Find tests to run
        tests_to_run = []
        
        # Direct mapping
        if file_path in self.test_mapping:
            tests_to_run.extend(self.test_mapping[file_path])
        else:
            # If no direct mapping, try to find a match for test files
            filename = os.path.basename(file_path)
            if filename.startswith('test_'):
                tests_to_run.append(file_path)
            else:
                # For source files without direct mapping, run all tests
                print(f"No specific tests mapped for {file_path}, running all tests")
                tests_to_run = ['test_timescale_analyzer_unit.py', 
                              'test_timescale_analyzer_integration.py',
                              'test_financial_accuracy.py', 
                              'test_timescale_analyzer_edge_cases.py']
        
        # Run the tests
        if tests_to_run:
            print(f"Running tests: {', '.join(tests_to_run)}")
            print("-" * 70)
            
            try:
                # Option 1: Run with unittest
                for test_file in tests_to_run:
                    cmd = [sys.executable, '-m', 'unittest', test_file]
                    subprocess.run(cmd)
                
                # Option 2: Alternative with pytest
                # cmd = [sys.executable, '-m', 'pytest'] + tests_to_run + ['-v']
                # subprocess.run(cmd)
                
            except Exception as e:
                print(f"Error running tests: {str(e)}")
            
            print("\n" + "=" * 70)
        else:
            print("No tests to run for this file")
            print("\n" + "=" * 70)

def start_watching():
    """Start watching for file changes"""
    path = os.path.dirname(os.path.abspath(__file__))
    event_handler = TestRunner()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    
    print("=" * 70)
    print("VariancePro Continuous Test Runner")
    print("=" * 70)
    print(f"Watching for changes in: {path}")
    print("Press Ctrl+C to stop")
    print("=" * 70)
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watching()
