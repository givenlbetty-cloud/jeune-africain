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

python manage.py create_superuser_env
