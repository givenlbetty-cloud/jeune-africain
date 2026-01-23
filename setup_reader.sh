#!/bin/bash

# 🚀 BNC eBook Reader - Quick Start Setup
# Script de configuration rapide du lecteur amélioré

set -e

echo "📖 BNC eBook Reader - Quick Start Setup"
echo "========================================"
echo ""

# Vérification de Django
echo "🔍 Vérification de Django..."
if ! python manage.py --version &> /dev/null; then
    echo "❌ Django non trouvé. Assurez-vous d'être dans l'environnement virtualenv"
    exit 1
fi
echo "✅ Django trouvé"

# Validation
echo ""
echo "🧪 Validation des améliorations..."
if python validate_reader_improvements.py > /dev/null 2>&1; then
    echo "✅ Validation réussie!"
else
    echo "⚠️  Validation échouée. Vérifiez les erreurs."
    python validate_reader_improvements.py
    exit 1
fi

# Migrations
echo ""
echo "📚 Vérification des migrations..."
if python manage.py migrate --plan 2>/dev/null | grep -q "reading_session"; then
    echo "⚠️  Migrations de ReadingSession en attente"
    read -p "Appliquer les migrations? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📝 Application des migrations..."
        python manage.py migrate
        echo "✅ Migrations appliquées"
    fi
else
    echo "✅ Migrations à jour"
fi

# Collecte statiques
echo ""
echo "🎨 Collecte des fichiers statiques..."
if [ "$1" = "--production" ]; then
    python manage.py collectstatic --noinput
    echo "✅ Fichiers statiques collectés (production)"
else
    echo "ℹ️  Statiques auto en développement"
fi

# Tests
echo ""
echo "🧪 Exécution des tests..."
read -p "Exécuter les tests du lecteur? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py test catalogue.test_ebook_reader -v 2
    echo "✅ Tests réussis!"
else
    echo "⏭️  Tests skippés"
fi

# Summary
echo ""
echo "========================================"
echo "✨ Setup Complet! ✨"
echo "========================================"
echo ""
echo "📚 Documentation:"
echo "  - EBOOK_READER_GUIDE.md (Utilisation)"
echo "  - READER_INSTALLATION_GUIDE.md (Installation)"
echo "  - READER_IMPROVEMENTS_COMPLETE.md (Détails techniques)"
echo ""
echo "🚀 Démarrer le serveur:"
echo "  python manage.py runserver"
echo ""
echo "🎨 Tester le lecteur:"
echo "  1. Ouvrir http://localhost:8000/catalogue/"
echo "  2. Cliquer sur un livre"
echo "  3. Cliquer sur 'Lire'"
echo ""
echo "📖 Tester les features:"
echo "  - Sélectionnez du texte → Menu surlignage"
echo "  - Appuyez sur Ctrl+N → Ajouter note"
echo "  - Appuyez sur Ctrl+B → Marque-pages"
echo "  - Appuyez sur → ou Espace → Page suivante"
echo ""
echo "✅ Vous êtes prêt!"
