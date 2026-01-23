"""URLs pour les vues utilisateur."""

from django.urls import path
from users import views

app_name = 'users'

urlpatterns = [
    # Authentification
    path('login/', views.login_view, name='login'),
    path('login/phone/', views.login_phone_view, name='login_phone'),  # Nouvelle route
    path('login/verify-otp/', views.verify_otp_view, name='verify_otp'),  # Nouvelle route
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profil et gestion
    path('profile/', views.profile_view, name='profile'),
    path('library/', views.my_library_view, name='my_library'),
    path('history/', views.reading_history_view, name='reading_history'),
    path('payments/', views.payment_history_view, name='payment_history'),
    path('favorites/', views.favorite_list_view, name='favorite_list'),
    path('notes/', views.note_list_view, name='note_list'),
    path('highlights/', views.highlight_list_view, name='highlight_list'),
    
    # Langue / i18n
    path('set-language/', views.set_language_view, name='set_language'),
]
