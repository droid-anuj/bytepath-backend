#!/bin/bash
# Convert Firebase credentials to base64 for environment variable

if [ ! -f "serviceAccountKey.json" ]; then
    echo "❌ serviceAccountKey.json not found!"
    exit 1
fi

echo "🔐 Converting Firebase credentials to base64..."

base64 -w 0 serviceAccountKey.json > firebase_creds_base64.txt

echo "✅ Conversion complete!"
echo ""
echo "📋 Copy the content of firebase_creds_base64.txt"
echo "   and set it as FIREBASE_CREDENTIALS_BASE64 environment variable"
echo ""
echo "To view the content:"
echo "  cat firebase_creds_base64.txt"
