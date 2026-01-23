"""
Modèle Commande - BNC Digital Library
Utilisé pour tracker les paiements Moneiro
"""

from django.db import models
from django.contrib.auth.models import User


class Commande(models.Model):
    """Modèle pour les commandes avec paiement Moneiro"""
    
    DEVISE_CHOICES = [
        ('USD', 'Dollar'),
        ('CDF', 'Franc Congolais'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('SUCCESS', 'Payée'),
        ('FAILED', 'Échouée'),
        ('CANCELLED', 'Annulée'),
    ]
    
    # Commande
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commandes')
    reference = models.CharField(max_length=100, unique=True)  # ID unique pour Moneiro
    
    # Paiement
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    devise = models.CharField(max_length=3, choices=DEVISE_CHOICES, default='USD')
    est_payee = models.BooleanField(default=False)
    
    # Produit
    book = models.ForeignKey('catalogue.Book', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=255, blank=True)
    
    # Méthode paiement
    methode_paiement = models.CharField(
        max_length=50, 
        choices=[
            ('mpesa', 'M-Pesa'),
            ('orange_money', 'Orange Money'),
            ('airtel_money', 'Airtel Money'),
            ('visa', 'Visa'),
            ('mastercard', 'Mastercard'),
        ],
        blank=True
    )
    
    # Statut
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        app_label = 'catalogue'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Commande {self.reference} - {self.montant} {self.devise}"
    
    def marquer_comme_payee(self, transaction_id=None):
        """Marquer la commande comme payée"""
        self.est_payee = True
        self.status = 'SUCCESS'
        if transaction_id:
            self.transaction_id = transaction_id
        
        from django.utils import timezone
        self.paid_at = timezone.now()
        self.save()
