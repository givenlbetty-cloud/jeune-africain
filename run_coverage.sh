#!/bin/bash
# Test Coverage Generation
# Génération de rapports de couverture

echo "=========================================="
echo "Django BNC - Test Coverage Report"
echo "=========================================="
echo

# Run tests with coverage
echo "Running tests with coverage..."
coverage run --source='catalogue' manage.py test catalogue.tests -v 0

echo
echo "Generating coverage report..."
coverage report -m

echo
echo "Generating HTML report in htmlcov/..."
coverage html

echo
echo "=========================================="
echo "Coverage Report Complete"
echo "HTML report available at: htmlcov/index.html"
echo "=========================================="
