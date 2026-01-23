from django.apps import AppConfig

class CatalogueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catalogue'
    verbose_name = '📖 Catalogue'
    
    def ready(self):
        """Enregistrer les signaux Django"""
        import catalogue.signals  # noqa

class MediaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catalogue.media_app' # Point to the dummy module
    label = 'media_management' # Virtual Model Group
    verbose_name = '📺 Gestion Média'

class FinanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catalogue.finance_app'
    label = 'finance_management'
    verbose_name = '💳 Finance & Paiement'

class EventsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catalogue.events_app'
    label = 'event_management'
    verbose_name = '📅 Événements'

