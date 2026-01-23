"""
PayPal Payment URLs
"""

from django.urls import path
from . import payment_paypal_webhook

app_name = 'payment_paypal'

urlpatterns = [
    # PayPal webhook endpoint
    path('api/webhooks/paypal/', 
         payment_paypal_webhook.paypal_webhook, 
         name='webhook'),
]
