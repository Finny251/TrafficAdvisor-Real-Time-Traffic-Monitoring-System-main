#!/bin/bash
set -e

echo "=== Starting Flask App ==="

export FLASK_APP=traffic.py
export FLASK_ENV=development

flask run --host=0.0.0.0 --port=8080
