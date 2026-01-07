#!/bin/bash
# Chess Puzzle Generator - Run Script
# Sets required environment variables for Cairo library

# Activate virtual environment
source venv/bin/activate

# Set library path for Cairo
export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib

# Run the application
python main.py
