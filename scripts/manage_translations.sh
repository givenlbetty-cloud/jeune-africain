#!/bin/bash
##############################################################################
# Script de gestion des traductions i18n
# Usage: ./scripts/manage_translations.sh [command]
# Commands: extract, compile, update, status, add-language
##############################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MANAGE_PY="$PROJECT_DIR/manage.py"

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# FONCTIONS
# ============================================================================

print_header() {
    echo -e "${BLUE}▸ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Vérifier que Django est installé
check_django() {
    if ! command -v python &> /dev/null; then
        print_error "Python n'est pas installé"
        exit 1
    fi
    
    if ! python -c "import django" 2>/dev/null; then
        print_error "Django n'est pas installé"
        exit 1
    fi
}

# Extraire les strings à traduire
extract_messages() {
    print_header "Extraction des messages..."
    
    cd "$PROJECT_DIR"
    python "$MANAGE_PY" makemessages -a --keep-pot
    
    if [ $? -eq 0 ]; then
        print_success "Messages extraits avec succès"
        echo "Fichiers .po générés dans: locale/[LANG]/LC_MESSAGES/"
    else
        print_error "Erreur lors de l'extraction"
        exit 1
    fi
}

# Compiler les traductions
compile_messages() {
    print_header "Compilation des traductions..."
    
    cd "$PROJECT_DIR"
    python "$MANAGE_PY" compilemessages
    
    if [ $? -eq 0 ]; then
        print_success "Traductions compilées"
        echo "Fichiers .mo générés dans: locale/[LANG]/LC_MESSAGES/"
    else
        print_error "Erreur lors de la compilation"
        exit 1
    fi
}

# Mettre à jour tous les fichiers .po
update_translations() {
    print_header "Mise à jour des traductions..."
    
    extract_messages
    compile_messages
    
    print_success "Traductions mises à jour"
}

# Afficher le statut des traductions
show_status() {
    print_header "Statut des traductions..."
    
    if [ ! -d "$PROJECT_DIR/locale" ]; then
        print_warning "Aucun répertoire locale/ trouvé"
        return
    fi
    
    echo ""
    echo "Langues disponibles:"
    for lang_dir in "$PROJECT_DIR/locale"/*/; do
        lang=$(basename "$lang_dir")
        po_file="$lang_dir/LC_MESSAGES/django.po"
        mo_file="$lang_dir/LC_MESSAGES/django.mo"
        
        if [ -f "$po_file" ]; then
            po_size=$(wc -l < "$po_file")
            translated=$(grep -c "^msgstr" "$po_file" || echo 0)
            
            if [ -f "$mo_file" ]; then
                status="${GREEN}✓${NC}"
            else
                status="${YELLOW}⚠${NC}"
            fi
            
            printf "  $status ${BLUE}%s${NC}: %d lignes, %d traductions\n" "$lang" "$po_size" "$translated"
        fi
    done
    
    echo ""
}

# Ajouter une nouvelle langue
add_language() {
    if [ -z "$1" ]; then
        print_error "Code langue requis (ex: es, de, it)"
        exit 1
    fi
    
    lang=$1
    print_header "Ajout de la langue: $lang"
    
    cd "$PROJECT_DIR"
    python "$MANAGE_PY" makemessages -l "$lang"
    
    if [ $? -eq 0 ]; then
        print_success "Langue $lang ajoutée"
        echo "Éditez: locale/$lang/LC_MESSAGES/django.po"
        echo "Puis compilez avec: $0 compile"
    else
        print_error "Erreur lors de l'ajout"
        exit 1
    fi
}

# Valider les fichiers .po
validate_po_files() {
    print_header "Validation des fichiers .po..."
    
    errors=0
    
    for po_file in "$PROJECT_DIR"/locale/*/LC_MESSAGES/django.po; do
        if ! msgfmt -c -v "$po_file" 2>/dev/null; then
            print_error "Erreur dans: $po_file"
            ((errors++))
        fi
    done
    
    if [ $errors -eq 0 ]; then
        print_success "Tous les fichiers .po sont valides"
    else
        print_error "$errors fichier(s) avec erreurs"
        exit 1
    fi
}

# Générer un rapport
generate_report() {
    print_header "Génération du rapport de traductions..."
    
    report_file="$PROJECT_DIR/TRANSLATIONS_REPORT.md"
    
    {
        echo "# 📊 Rapport des Traductions"
        echo ""
        echo "Généré le: $(date)"
        echo ""
        echo "## Langues Supportées"
        echo ""
        
        for lang_dir in "$PROJECT_DIR"/locale/*/; do
            lang=$(basename "$lang_dir")
            po_file="$lang_dir/LC_MESSAGES/django.po"
            
            if [ -f "$po_file" ]; then
                total=$(grep -c "^msgid" "$po_file" || echo 0)
                translated=$(grep "^msgstr \"[^\"]*\"" "$po_file" | grep -v "^msgstr \"\"" | wc -l)
                percent=$((translated * 100 / total))
                
                echo "### $lang"
                echo ""
                echo "- **Complétude:** $percent% ($translated/$total)"
                echo ""
            fi
        done
        
        echo "## Fichiers à Traduire"
        echo ""
        find "$PROJECT_DIR" -type f \( -name "*.py" -o -name "*.html" \) | while read file; do
            if grep -q "_(" "$file" 2>/dev/null || grep -q "{% trans" "$file" 2>/dev/null; then
                echo "- $(basename "$file")"
            fi
        done
        
    } > "$report_file"
    
    print_success "Rapport généré: $report_file"
}

# ============================================================================
# MAIN
# ============================================================================

check_django

case "${1:-help}" in
    extract)
        extract_messages
        ;;
    compile)
        compile_messages
        ;;
    update)
        update_translations
        ;;
    validate)
        validate_po_files
        ;;
    status)
        show_status
        ;;
    add)
        add_language "$2"
        ;;
    report)
        generate_report
        ;;
    all)
        update_translations
        validate_po_files
        show_status
        generate_report
        ;;
    help|*)
        cat << EOF
${BLUE}📝 Gestionnaire de Traductions BNC${NC}

${GREEN}Usage:${NC}
  ./scripts/manage_translations.sh [command]

${GREEN}Commands:${NC}
  extract           Extraire les strings à traduire
  compile           Compiler les .po en .mo
  update            Extract + Compile (recommandé)
  validate          Valider tous les fichiers .po
  status            Afficher le statut des traductions
  add [code]        Ajouter une nouvelle langue (ex: es, de)
  report            Générer un rapport
  all               Tout faire (extract, compile, validate, status, report)
  help              Afficher cette aide

${GREEN}Exemples:${NC}
  ./scripts/manage_translations.sh update
  ./scripts/manage_translations.sh add es
  ./scripts/manage_translations.sh status

${BLUE}Langues supportées:${NC}
  fr  Français (défaut)
  en  Anglais
  ar  Arabe
  pt  Portugais
  sw  Swahili

${YELLOW}Notes:${NC}
  • Éditez locale/[LANG]/LC_MESSAGES/django.po après extraction
  • Les fichiers .mo sont générés par compile
  • Utilisez 'all' avant chaque déploiement
EOF
        ;;
esac
