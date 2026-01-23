"""
URLs pour les webhooks de paiement.
À inclure dans le urls.py principal du projet.

Usage in main urls.py:
    from django.urls import path, include
    
    urlpatterns = [
        ...
        path('api/payments/', include('catalogue.payment_webhook_urls')),
    ]
"""

from django.urls import path
from catalogue.payment_webhooks import (
    stripe_webhook,
    paypal_webhook,
    airtel_money_webhook,
    mpesa_webhook,
)
from catalogue.views_moneroo import moneroo_callback

app_name = 'payment_webhooks'

urlpatterns = [
    # Moneroo webhook
    path('moneroo-callback/', moneroo_callback, name='moneroo_webhook'),

    # Stripe webhook
    path('stripe/webhook/', stripe_webhook, name='stripe_webhook'),
    
    # PayPal webhook
    path('paypal/webhook/', paypal_webhook, name='paypal_webhook'),
    
    # Mobile Money webhooks
    path('airtel/webhook/', airtel_money_webhook, name='airtel_webhook'),
    path('mpesa/webhook/', mpesa_webhook, name='mpesa_webhook'),
]
