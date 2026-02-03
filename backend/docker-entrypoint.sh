#!/bin/bash
set -e

echo "Checking and installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "Starting application..."
exec "$@"
