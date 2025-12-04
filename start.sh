#!/bin/bash
# Quick start script for local development

echo "🚀 Starting PrepShark Django Backend..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Run development server
echo "✅ Starting server at http://localhost:8000"
echo "📊 Admin panel: http://localhost:8000/admin/"
echo "📡 API: http://localhost:8000/api/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python manage.py runserver
