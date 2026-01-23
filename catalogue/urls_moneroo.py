"""
Moneroo Payment URLs
Clean and minimal routing for Moneroo payment integration
"""

from django.urls import path
from . import views_moneroo

app_name = 'moneroo'

urlpatterns = [
    # Payment form display
    path('payment/initiate/', 
         views_moneroo.payment_form, 
         name='payment_form'),
    
    # Payment initiation (POST)
    path('payment/create/', 
         views_moneroo.initiate_moneroo_payment, 
         name='initiate_payment'),
    
    # Moneroo webhook callback
    path('payment/moneroo-callback/', 
         views_moneroo.moneroo_callback, 
         name='callback'),
    
    # Return page after payment
    path('payment/callback/', 
         views_moneroo.payment_callback, 
         name='return'),
]

# ════════════════════════════════════════════════════════════════════════
# HOW TO INCLUDE IN MAIN urls.py:
# ════════════════════════════════════════════════════════════════════════

"""
from django.urls import path, include

urlpatterns = [
    # ... other URLs ...
    path('', include('catalogue.urls_moneroo')),
]
"""
