#!/bin/bash
set -e  # Exit on error

# Install dependencies
pip install -r requirements.txt

flask db init

flask db migrate -m "init"

# Run migrations
flask db upgrade
