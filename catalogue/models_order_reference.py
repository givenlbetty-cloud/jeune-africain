"""
Order Model Reference for Moneroo Integration
Add this to your models.py or adapt to your existing Order model
"""

from django.db import models
from django.contrib.auth.models import User


class Order(models.Model):
    """Order model for Moneroo payment tracking"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('mobile_money', 'Mobile Money (M-Pesa, Orange, Airtel)'),
        ('card', 'Card (Visa, Mastercard)'),
    ]
    
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('CDF', 'Congolese Franc'),
    ]
    
    # Core fields
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    reference = models.CharField(max_length=100, unique=True)
    
    # Payment information
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    
    # Product
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    is_paid = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.reference} - {self.amount} {self.currency} ({self.status})"
    
    def mark_as_completed(self, transaction_id=None):
        """Mark order as completed after successful payment"""
        from django.utils import timezone
        
        self.status = 'COMPLETED'
        self.is_paid = True
        self.paid_at = timezone.now()
        
        if transaction_id:
            self.transaction_id = transaction_id
        
        self.save()
    
    def mark_as_failed(self):
        """Mark order as failed"""
        self.status = 'FAILED'
        self.is_paid = False
        self.save()
