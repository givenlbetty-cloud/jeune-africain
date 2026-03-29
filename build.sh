#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Créer le dossier media sur le disque persistant si on est sur Render
if [ -n "$RENDER_MEDIA_ROOT" ]; then
    mkdir -p "$RENDER_MEDIA_ROOT"
    echo "✅ Media directory ready: $RENDER_MEDIA_ROOT"
fi

python manage.py collectstatic --no-input
python manage.py migrate

# Backup automatique après migration (sauvegardé sur le disque persistant si disponible)
if [ -n "$RENDER_MEDIA_ROOT" ]; then
    mkdir -p "$RENDER_MEDIA_ROOT/backups"
    python manage.py backup_data -o "$RENDER_MEDIA_ROOT/backups/backup_$(date +%Y%m%d_%H%M%S).json" || true
    echo "✅ Backup saved to persistent disk"
fi

echo "🔑 Creating superuser..."
echo "   DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-(⚠️ NOT SET)}"
echo "   DJANGO_SUPERUSER_PASSWORD=$(if [ -n \"$DJANGO_SUPERUSER_PASSWORD\" ]; then echo '✅ SET'; else echo '⚠️ NOT SET'; fi)"
echo "   DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME:-admin}"
python manage.py create_superuser_env 2>&1 || echo "⚠️ Superuser creation failed (will retry at startup)"
