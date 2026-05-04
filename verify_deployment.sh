#!/usr/bin/env bash
# Verification script for GMAO ENIB deployment

echo "================================"
echo "GMAO ENIB Deployment Verification"
echo "================================"

echo ""
echo "✓ Checking migrations..."

echo ""
echo "Equipment migrations:"
ls -la equipment/migrations/0002*.py equipment/migrations/0003*.py equipment/migrations/0004*.py 2>/dev/null | awk '{print "  " $9}'

echo ""
echo "Maintenance migrations:"
ls -la maintenance/migrations/0003*.py maintenance/migrations/0004*.py 2>/dev/null | awk '{print "  " $9}'

echo ""
echo "✓ Checking static files..."
if [ -f "static/images/enib_logo.svg" ]; then
    echo "  ✓ ENIB logo found"
else
    echo "  ✗ ENIB logo NOT found"
fi

echo ""
echo "✓ Checking template updates..."
if grep -q "enib_logo.svg" templates/base.html; then
    echo "  ✓ Logo integrated in base.html"
else
    echo "  ✗ Logo NOT found in base.html"
fi

echo ""
echo "✓ Checking CSS updates..."
if grep -q "enib-logo-img" static/css/app.css; then
    echo "  ✓ CSS styling for logo found"
else
    echo "  ✗ CSS styling NOT found"
fi

echo ""
echo "✓ Checking seed data..."
if grep -q '"priority": "Normal"' maintenance/management/commands/seed_demo_data.py; then
    echo "  ✓ Seed data updated with new priorities"
else
    echo "  ✗ Seed data NOT updated"
fi

echo ""
echo "✓ Running Django system checks..."
python manage.py check

echo ""
echo "✓ Checking for migration issues..."
python manage.py makemigrations --dry-run

echo ""
echo "================================"
echo "Verification Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Review CHANGES.md for detailed information"
echo "2. Run: git add ."
echo "3. Run: git commit -m 'Apply ENIB logo and fix duplicate fields'"
echo "4. Run: git push origin main"
echo "5. Check Render deployment logs"
