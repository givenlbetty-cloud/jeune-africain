#!/bin/bash
# Test simple des 10 phases

cd /workspaces/bnc

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║         VALIDATION DES 10 PHASES - RAPPORT COMPLET                         ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"

echo ""
echo "✓ Activation virtualenv..."
source venv/bin/activate 2>/dev/null

echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo "ÉTAPE 1: VÉRIFICATION DJANGO"
echo "════════════════════════════════════════════════════════════════════════════"
python manage.py check 2>&1 | grep -E "(OK|error|issue)"

echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo "ÉTAPE 2: VÉRIFICATION DES MODÈLES PAR PHASE"
echo "════════════════════════════════════════════════════════════════════════════"

python manage.py shell <<EOF
from django.apps import apps

phases = {
    'Phase 1 - Auth': ['auth.User', 'auth.Group'],
    'Phase 2 - Catalogue': ['catalogue.Book', 'catalogue.Author', 'catalogue.Category', 'catalogue.Review'],
    'Phase 3 - Panier': ['catalogue.ShoppingCart', 'catalogue.UserLibrary', 'catalogue.ReadingSession'],
    'Phase 4 - Paiements': ['catalogue.Payment', 'catalogue.Invoice', 'catalogue.Transaction'],
    'Phase 5 - Lecteur PDF': ['catalogue.Highlight', 'catalogue.Note', 'catalogue.Bookmark'],
    'Phase 6 - Analytics': ['catalogue.TrendingBook', 'catalogue.UserAnalytics', 'catalogue.ReadingActivity'],
    'Phase 7 - Forums': ['catalogue.ForumCategory', 'catalogue.Discussion', 'catalogue.Comment', 'catalogue.Vote'],
    'Phase 8 - Communauté': ['catalogue.Follow', 'catalogue.UserPreference', 'catalogue.SocialShare'],
    'Phase 9 - Médias': ['catalogue.AudioBook', 'catalogue.Video', 'catalogue.Podcast', 'catalogue.MediaProgress'],
    'Phase 10 - Recommandations': ['catalogue.UserRecommendation', 'catalogue.Event'],
}

passed = 0
failed = 0

for phase_name, models in phases.items():
    all_exist = True
    for model_path in models:
        try:
            app_label, model_name = model_path.rsplit('.', 1)
            apps.get_model(app_label, model_name)
        except:
            all_exist = False
            break
    
    if all_exist:
        print(f"✅ {phase_name}: OK")
        passed += 1
    else:
        print(f"❌ {phase_name}: ERREUR")
        failed += 1

print("")
print("════════════════════════════════════════════════════════════════════════════")
print(f"RÉSUMÉ: {passed}/10 phases validées")
print("════════════════════════════════════════════════════════════════════════════")

if passed == 10:
    print("🎉 EXCELLENT! Toutes les 10 phases sont implémentées!")
else:
    print(f"⚠️  {failed} phase(s) manquante(s) ou incomplète(s)")
EOF

echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo "ÉTAPE 3: VÉRIFICATION DES DONNÉES"
echo "════════════════════════════════════════════════════════════════════════════"

python manage.py shell <<EOF
from catalogue.models import Book, Author, Category, Payment, Review, ReadingSession

print(f"📚 Livres: {Book.objects.count()}")
print(f"✍️  Auteurs: {Author.objects.count()}")
print(f"📖 Catégories: {Category.objects.count()}")
print(f"💳 Paiements: {Payment.objects.count()}")
print(f"⭐ Avis: {Review.objects.count()}")
print(f"📕 Sessions lecture: {ReadingSession.objects.count()}")
EOF

echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo "ÉTAPE 4: VÉRIFICATION DES TESTS"
echo "════════════════════════════════════════════════════════════════════════════"

python manage.py test --verbosity=0 2>&1 | tail -5

echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo "VALIDATION TERMINÉE ✅"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""
echo "Pour plus de détails, consultez:"
echo "  - GUIDE_VALIDATION_10_PHASES.md"
echo "  - RAPPORT_CAHIER_DES_CHARGES_FINAL.md"
echo "  - test_all_phases.py (script avancé)"
