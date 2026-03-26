"""
Donation URLs
"""

from django.urls import path
from catalogue import views_donation

app_name = 'donation'

urlpatterns = [
    path('donation/', views_donation.donation_view, name='donate'),
    path('donation/merci/<uuid:donation_id>/', views_donation.donation_thank_you, name='merci'),
]
