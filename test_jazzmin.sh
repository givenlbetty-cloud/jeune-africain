#!/bin/bash

# 🔍 Script de diagnostic Jazzmin complet

cd /workspaces/bnc
source venv/bin/activate

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║       🔍 DIAGNOSTIC COMPLET JAZZMIN                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 1. Versions
echo "1️⃣  VERSIONS INSTALLÉES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python -c "import django; print(f'✅ Django: {django.VERSION}')"
python -c "import jazzmin; print(f'✅ Jazzmin: {jazzmin.__version__}')"
python -c "import import_export; print(f'✅ django-import-export installé')"
echo ""

# 2. Configuration Django
echo "2️⃣  CONFIGURATION DJANGO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python manage.py check
echo ""

# 3. INSTALLED_APPS
echo "3️⃣  INSTALLED_APPS (ordre correct?)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python manage.py shell -c "
from django.conf import settings
apps = settings.INSTALLED_APPS
for i, app in enumerate(apps[:10], 1):
    marker = '✅ [FIRST]' if i == 1 and 'jazzmin' in app else '✅'
    print(f'{i:2d}. {marker} {app}')
print('...')
"
echo ""

# 4. AUTH_USER_MODEL
echo "4️⃣  AUTH_USER_MODEL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python manage.py shell -c "
from django.conf import settings
print(f'✅ AUTH_USER_MODEL = {settings.AUTH_USER_MODEL}')
"
echo ""

# 5. Migrations
echo "5️⃣  MIGRATIONS APPLIQUÉES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python manage.py migrate --check && echo "✅ Toutes les migrations appliquées"
echo ""

# 6. Fichiers statiques
echo "6️⃣  FICHIERS STATIQUES JAZZMIN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -d "staticfiles/jazzmin" ]; then
    count=$(find staticfiles/jazzmin -type f | wc -l)
    echo "✅ Fichiers Jazzmin: $count fichiers"
else
    echo "❌ Dossier staticfiles/jazzmin manquant - à exécuter:"
    echo "   python manage.py collectstatic --noinput"
fi
echo ""

# 7. Superuser
echo "7️⃣  SUPERUSER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
admins = User.objects.filter(is_superuser=True)
if admins.exists():
    for admin in admins:
        print(f'✅ Superuser: {admin.email} ({admin.get_role_display()})')
else:
    print('❌ Aucun superuser trouvé')
"
echo ""

# 8. Modèles chargés
echo "8️⃣  MODÈLES DJANGO CHARGÉS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python manage.py shell -c "
from django.apps import apps
apps_list = apps.get_app_configs()
for app in apps_list:
    models_count = len(app.get_models())
    if models_count > 0:
        print(f'✅ {app.name}: {models_count} modèles')
"
echo ""

# 9. Résumé
echo "╔════════════════════════════════════════════════════════════╗"
echo "║        ✅ DIAGNOSTIC COMPLET                              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 Pour accéder à Jazzmin:"
echo "   URL: http://localhost:8000/admin/"
echo "   Email: admin@bnc.local"
echo "   Password: admin123"
echo ""
echo "🚀 Pour démarrer le serveur:"
echo "   python manage.py runserver 0.0.0.0:8000"
echo ""

