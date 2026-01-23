#!/bin/bash
# Script de vérification du redesign UI/UX

echo "=================================================="
echo "🎨 VÉRIFICATION DU REDESIGN UI/UX BNC"
echo "=================================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Compteurs
total=0
passed=0
failed=0

# Fonction de test
test_item() {
    local name=$1
    local condition=$2
    total=$((total+1))
    
    if [ "$condition" -eq 0 ]; then
        echo -e "${GREEN}✅${NC} $name"
        passed=$((passed+1))
    else
        echo -e "${RED}❌${NC} $name"
        failed=$((failed+1))
    fi
}

echo "📋 Tests des fichiers..."
echo ""

# Test 1: Fichiers principaux
[ -f "/workspaces/bnc/templates/base.html" ] && test_item "base.html existe" 0 || test_item "base.html existe" 1
[ -f "/workspaces/bnc/templates/home.html" ] && test_item "home.html existe" 0 || test_item "home.html existe" 1
[ -f "/workspaces/bnc/templates/catalogue/catalogue.html" ] && test_item "catalogue.html existe" 0 || test_item "catalogue.html existe" 1
[ -f "/workspaces/bnc/templates/catalogue/book_reader.html" ] && test_item "book_reader.html existe" 0 || test_item "book_reader.html existe" 1
[ -f "/workspaces/bnc/static/css/global.css" ] && test_item "global.css existe" 0 || test_item "global.css existe" 1

echo ""
echo "📝 Tests des contenus..."
echo ""

# Test 2: Contenus des templates
curl -s http://localhost:8000/ | grep -q "<title>BNC - Accueil</title>"
test_item "Accueil a le bon titre" $?

curl -s http://localhost:8000/ | grep -q "Bienvenue sur BNC"
test_item "Accueil affiche 'Bienvenue sur BNC'" $?

curl -s http://localhost:8000/books/ | grep -q "<title>Catalogue - BNC</title>"
test_item "Catalogue a le bon titre" $?

curl -s http://localhost:8000/ | grep -q "data-bs-theme"
test_item "Support mode sombre détecté" $?

curl -s http://localhost:8000/ | grep -q "themeToggle"
test_item "Toggle theme détecté" $?

curl -s http://localhost:8000/ | grep -q "navbar-brand"
test_item "Navbar présente" $?

curl -s http://localhost:8000/ | grep -q "<footer"
test_item "Footer présent" $?

echo ""
echo "🎨 Tests du design..."
echo ""

# Test 3: Classes CSS
curl -s http://localhost:8000/ | grep -q "hero-section"
test_item "Hero section présente" $?

curl -s http://localhost:8000/books/ | grep -q "book-grid"
test_item "Grille de livres détectée" $?

curl -s http://localhost:8000/books/ | grep -q "filter-card"
test_item "Filtres présents" $?

curl -s http://localhost:8000/ | grep -q "fade-in-up"
test_item "Animations fade-in-up détectées" $?

echo ""
echo "🌐 Tests des fonctionnalités..."
echo ""

# Test 4: Fonctionnalités
curl -s http://localhost:8000/books/ | grep -q "form-control"
test_item "Formulaires présents" $?

curl -s http://localhost:8000/books/ | grep -q "pagination"
test_item "Pagination présente" $?

curl -s http://localhost:8000/ | grep -q "btn-primary"
test_item "Boutons primaires présents" $?

curl -s http://localhost:8000/ | grep -q "fas fa-"
test_item "Icons Font Awesome détectées" $?

echo ""
echo "📱 Tests responsiveness..."
echo ""

# Test 5: Responsive
curl -s http://localhost:8000/ | grep -q "viewport"
test_item "Viewport meta tag présent" $?

curl -s http://localhost:8000/ | grep -q "col-md\|col-lg"
test_item "Classes Bootstrap responsives détectées" $?

curl -s http://localhost:8000/ | grep -q "navbar-toggler"
test_item "Hamburger menu présent (mobile)" $?

echo ""
echo "🔐 Tests de sécurité..."
echo ""

# Test 6: Sécurité
curl -s http://localhost:8000/ | grep -q "csrf"
test_item "CSRF token présent" $?

curl -s http://localhost:8000/ | grep -q "meta charset"
test_item "Charset déclaré" $?

echo ""
echo "=================================================="
echo "📊 RÉSULTATS"
echo "=================================================="
echo ""
echo -e "Total tests: $total"
echo -e "${GREEN}Réussis: $passed${NC}"
echo -e "${RED}Échoués: $failed${NC}"
echo ""

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}✅ TOUS LES TESTS SONT PASSÉS!${NC}"
    echo ""
    echo "🎉 Le redesign UI/UX est prêt pour la production!"
    exit 0
else
    echo -e "${YELLOW}⚠️  $failed test(s) ont échoué${NC}"
    exit 1
fi
