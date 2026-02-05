#!/bin/bash
set -e

echo "Checking for Python 3..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

python3 generate-data.py

echo ""
echo "Data generation complete!"
echo "CSV files are ready in the data/ directory."
