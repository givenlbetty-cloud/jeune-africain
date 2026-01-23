"""
Configuration des routes Moneiro
Ajoute ceci à ton urls.py principal
"""

from django.urls import path
from catalogue.views_moneiro import (
    process_payment,
    moneiro_webhook,
    paiement_succes,
    paiement_annule,
)

urlpatterns = [
    # Endpoints paiement
    path('process-payment/', process_payment, name='process_payment'),
    path('webhook-moneiro/', moneiro_webhook, name='moneiro_webhook'),
    
    # Pages retour
    path('paiement-succes/', paiement_succes, name='paiement_succes'),
    path('paiement-annule/', paiement_annule, name='paiement_annule'),
]

# ════════════════════════════════════════════════════════════════════════
# À AJOUTER DANS TON urls.py PRINCIPAL:
# ════════════════════════════════════════════════════════════════════════

"""
from django.urls import path, include

urlpatterns = [
    # ... autres URLs ...
    
    # URLs Moneiro
    path('', include('catalogue.urls_moneiro')),
]
"""
