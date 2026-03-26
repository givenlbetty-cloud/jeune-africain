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
python manage.py create_superuser_env
