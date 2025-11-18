#!/bin/bash

echo "🚀 Starting Bond Management System Backend..."
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -q fastapi uvicorn sqlalchemy psycopg2-binary python-dateutil pandas python-multipart

# Run migrations if needed
echo ""
echo "Checking database..."
python scripts/migrate_add_bond_issues.py --auto 2>&1 | grep -E "(Created table|Migration completed|already exists)" || true

# Start the server
echo ""
echo "Starting server at http://localhost:8000..."
echo "API Docs: http://localhost:8000/api/docs"
echo ""
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
