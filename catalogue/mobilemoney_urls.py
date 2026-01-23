"""
URLs pour le flux de paiement Mobile Money
"""

from django.urls import path
from catalogue.mobilemoney_views import (
    mobilemoney_payment_flow,
    mobilemoney_confirmation,
    mobilemoney_verify_otp,
    mobilemoney_check_status,
    mobilemoney_success,
    mobilemoney_failed,
)

app_name = 'mobilemoney'

urlpatterns = [
    # Flux principal
    path('pay/<uuid:book_id>/', mobilemoney_payment_flow, name='payment_flow'),
    path('confirmation/<uuid:payment_id>/', mobilemoney_confirmation, name='confirmation'),
    
    # Vérification OTP
    path('verify-otp/<uuid:payment_id>/', mobilemoney_verify_otp, name='verify_otp'),
    path('check-status/<uuid:payment_id>/', mobilemoney_check_status, name='check_status'),
    
    # Pages finales
    path('success/<uuid:payment_id>/', mobilemoney_success, name='success'),
    path('failed/<uuid:payment_id>/', mobilemoney_failed, name='failed'),
]
