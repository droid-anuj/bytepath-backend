#!/bin/bash
# Export SQLite data for migration to PostgreSQL

echo "🔍 Exporting data from SQLite..."

# Export all data except system tables
python manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --exclude auth.permission \
  --exclude contenttypes \
  --exclude admin.logentry \
  --exclude sessions.session \
  --indent 2 \
  > data_backup.json

if [ $? -eq 0 ]; then
    echo "✅ Data exported successfully to data_backup.json"
    echo "📊 File size: $(du -h data_backup.json | cut -f1)"
    echo ""
    echo "Next steps:"
    echo "1. Keep this file safe - it contains all your data"
    echo "2. Deploy to Render/Railway"
    echo "3. Run: python manage.py loaddata data_backup.json (on production)"
else
    echo "❌ Export failed!"
    exit 1
fi
