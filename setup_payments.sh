#!/bin/bash
# Script de setup complet du système de paiements BNC
# Usage: bash setup_payments.sh

set -e

echo "🔧 =========================================="
echo "   BNC PAYMENT SYSTEM SETUP"
echo "=========================================="

# 1. Vérifier les pré-requis
echo ""
echo "📋 Étape 1: Vérification des pré-requis..."

if ! command -v python &> /dev/null; then
    echo "❌ Python non trouvé"
    exit 1
fi

if ! python -c "import stripe" 2>/dev/null; then
    echo "⚠️  Stripe non installé - installation..."
    pip install stripe requests
fi

echo "✅ Pré-requis OK"

# 2. Créer fichier .env s'il n'existe pas
echo ""
echo "🔐 Étape 2: Configuration des variables d'environnement..."

if [ ! -f .env ]; then
    echo "📝 Création de .env (copie de .env.example.payments)"
    cp .env.example.payments .env
    echo "⚠️  Important: Éditez .env avec vos vraies clés API!"
    echo "   nano .env"
fi

echo "✅ Configuration OK"

# 3. Vérifier Django
echo ""
echo "🐍 Étape 3: Vérification Django..."

python manage.py check
echo "✅ Django OK"

# 4. Appliquer les migrations
echo ""
echo "📦 Étape 4: Migrations..."

python manage.py migrate
echo "✅ Migrations appliquées"

# 5. Créer répertoire logs
echo ""
echo "📝 Étape 5: Création répertoires..."

mkdir -p logs/
touch logs/payments.log
echo "✅ Répertoires créés"

# 6. Exécuter les tests de paiement
echo ""
echo "🧪 Étape 6: Tests de paiement..."

echo "Exécution des tests..."
python manage.py test catalogue.tests.test_payments_complete -v 2 2>&1 | head -30

# 7. Setup OAuth (optionnel)
echo ""
echo "🔐 Étape 7: Setup OAuth (optionnel)..."
echo "Pour configurer Google OAuth:"
echo "  1. Aller sur: https://console.cloud.google.com/"
echo "  2. Créer projet et OAuth 2.0 credentials"
echo "  3. Exécuter: python manage.py setup_oauth --provider google --client-id YOUR_ID --client-secret YOUR_SECRET"
echo ""

# 8. Résumé
echo ""
echo "=========================================="
echo "✅ SETUP COMPLET!"
echo "=========================================="
echo ""
echo "📚 Prochaines étapes:"
echo "1. ✏️  Éditer .env avec clés réelles"
echo "   nano .env"
echo ""
echo "2. 🧪 Tester en sandbox:"
echo "   python manage.py reconcile_payments"
echo ""
echo "3. 🌐 Déployer:"
echo "   python manage.py migrate --noinput"
echo "   gunicorn config.wsgi --bind 0.0.0.0:8000"
echo ""
echo "📖 Documentation: PAYMENT_SYSTEM_COMPLETE_GUIDE.md"
echo ""
