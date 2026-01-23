from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'Gestion des Utilisateurs'
    
    def ready(self):
        """Enregistrer les signaux au démarrage"""
        import users.email_signals  # Import pour enregistrer les signaux
