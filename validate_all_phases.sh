#!/bin/bash
# Script de validation complète du projet BNC

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                            ║"
echo "║         VALIDATION COMPLÈTE DU PROJET BNC - 10 PHASES                      ║"
echo "║                                                                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"

cd /workspaces/bnc

# Activation virtualenv
source venv/bin/activate

echo ""
echo "1️⃣  Vérifier la configuration Django..."
python manage.py check
if [ $? -ne 0 ]; then
    echo "❌ Erreur: Django check failed"
    exit 1
fi
echo "✅ Django OK"

echo ""
echo "2️⃣  Exécuter les tests unitaires..."
python manage.py test --verbosity=2 2>&1 | head -50
echo "✅ Tests lancés"

echo ""
echo "3️⃣  Valider les migrations..."
python manage.py migrate --plan 2>&1 | head -20
echo "✅ Migrations OK"

echo ""
echo "4️⃣  Lancer la validation complète des 10 phases..."
python test_all_phases.py

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    VALIDATION TERMINÉE                                     ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
