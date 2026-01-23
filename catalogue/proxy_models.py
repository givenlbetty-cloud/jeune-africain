from django.db import models
from django.contrib import admin
from .models import AudiobookMetadata, VideoMaterial, Podcast, Payment, MerchantPaymentAccount, Event

# ==================== MEDIA PROXIES ====================

class AudiobookProxy(AudiobookMetadata):
    class Meta:
        proxy = True
        app_label = 'media_management'
        verbose_name = 'Audiobook'
        verbose_name_plural = 'Audiobooks'

class VideoProxy(VideoMaterial):
    class Meta:
        proxy = True
        app_label = 'media_management'
        verbose_name = 'Vidéo'
        verbose_name_plural = 'Vidéos'

class PodcastProxy(Podcast):
    class Meta:
        proxy = True
        app_label = 'media_management'
        verbose_name = 'Podcast'
        verbose_name_plural = 'Podcasts'

# ==================== FINANCE PROXIES ====================

class PaymentProxy(Payment):
    class Meta:
        proxy = True
        app_label = 'finance_management'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Historique des Paiements'

class MerchantAccountProxy(MerchantPaymentAccount):
    class Meta:
        proxy = True
        app_label = 'finance_management'
        verbose_name = 'Compte Marchand'
        verbose_name_plural = 'Comptes Marchands'

# ==================== EVENT PROXIES ====================

class EventProxy(Event):
    class Meta:
        proxy = True
        app_label = 'event_management'
        verbose_name = 'Événement'
        verbose_name_plural = 'Agenda Événements'
