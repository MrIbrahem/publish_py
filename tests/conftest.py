"""Configuration and fixtures for pytest"""
import sys
from pathlib import Path

# Get the project root directory (parent of pytests folder)
project_root = Path(__file__).parent.parent

# Add python_src to sys.path so we can import from 'src' as a package
python_src_path = project_root# / "python_src"
sys.path.insert(0, str(python_src_path))
