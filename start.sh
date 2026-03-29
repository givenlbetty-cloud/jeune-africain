#!/usr/bin/env bash
# Script de démarrage Render — crée le superuser puis lance gunicorn

echo "🚀 Démarrage de l'application..."

# Créer le superuser au démarrage (les variables d'env sont toujours disponibles ici)
echo "🔑 Vérification du superuser..."
python manage.py create_superuser_env 2>&1
echo "✅ Vérification superuser terminée"

# Lancer gunicorn
exec gunicorn config.wsgi:application
