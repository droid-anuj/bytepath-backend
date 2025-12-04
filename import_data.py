#!/usr/bin/env python
"""
One-time data import script for Render deployment.
This will run automatically during the build process.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command

def import_data():
    """Import data from data_backup.json if it exists and hasn't been imported yet."""
    data_file = 'data_backup.json'
    
    # Check if data file exists
    if not os.path.exists(data_file):
        print(f"⚠️  {data_file} not found. Skipping data import.")
        return
    
    # Check if data has already been imported
    from api.models import Question
    if Question.objects.exists():
        print("✅ Data already exists. Skipping import.")
        return
    
    print(f"📦 Importing data from {data_file}...")
    try:
        call_command('loaddata', data_file)
        print("✅ Data imported successfully!")
    except Exception as e:
        print(f"❌ Error importing data: {e}")
        # Don't fail the build if import fails
        pass

if __name__ == '__main__':
    import_data()
