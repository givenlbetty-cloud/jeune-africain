"""
PayPal Payment Integration Examples for BNC Digital Library

This module provides example views for integrating PayPal payments into Django.
"""

from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import View, TemplateView
from django.http import JsonResponse
from django.urls import path
from django.db import models

from catalogue.payment_paypal import PayPalClient, initiate_paypal_payment


# ============================================================================
# EXAMPLE MODELS (Adjust to match your actual models)
# ============================================================================

class ExampleOrder(models.Model):
    """Example Order model"""
    
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
    
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    book = models.ForeignKey('catalogue.Book', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'catalogue'


# ============================================================================
# EXAMPLE VIEWS
# ============================================================================

class InitiatePayPalPaymentView(LoginRequiredMixin, View):
    """
    View to initiate a PayPal payment for book purchase
    
    Usage in urls.py:
        path('purchase/<int:book_id>/paypal/', 
             InitiatePayPalPaymentView.as_view(), 
             name='initiate_paypal_payment'),
    
    Usage in template:
        <form method="post" action="{% url 'initiate_paypal_payment' book.id %}">
            {% csrf_token %}
            <button type="submit">Pay with PayPal</button>
        </form>
    """
    
    def post(self, request, book_id):
        """Initiate PayPal payment"""
        from catalogue.models import Book
        
        # Get book
        book = get_object_or_404(Book, id=book_id)
        
        # Determine price (could be from book model or calculation)
        price = Decimal('50.00')  # Example: $50 per book
        
        # Create order
        order = ExampleOrder.objects.create(
            user=request.user,
            book=book,
            amount=price,
            currency='USD',
            payment_status='PENDING'
        )
        
        # Build redirect URLs
        success_url = request.build_absolute_uri('/paypal/success/')
        cancel_url = request.build_absolute_uri('/paypal/cancel/')
        
        # Initiate PayPal payment
        success, approval_url, payment_id = initiate_paypal_payment(
            amount=price,
            currency='USD',
            description=f'Purchase of "{book.title}"',
            return_url=success_url,
            cancel_url=cancel_url,
            order_id=str(order.id),
            email=request.user.email
        )
        
        if success:
            # Redirect to PayPal
            return redirect(approval_url)
        else:
            return JsonResponse(
                {'error': 'Failed to initiate payment'}, 
                status=500
            )


class PayPalSuccessView(LoginRequiredMixin, TemplateView):
    """
    View called after successful PayPal payment
    
    Usage in urls.py:
        path('paypal/success/', 
             PayPalSuccessView.as_view(), 
             name='paypal_success'),
    
    PayPal will redirect to:
        /paypal/success/?paymentId=PAY-123&PayerID=PAYER-456
    """
    
    template_name = 'payment/paypal_success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        payment_id = self.request.GET.get('paymentId')
        payer_id = self.request.GET.get('PayerID')
        
        if payment_id and payer_id:
            try:
                # Execute payment
                client = PayPalClient()
                success, transaction_id = client.execute_payment(
                    payment_id, 
                    payer_id
                )
                
                if success:
                    context['payment_success'] = True
                    context['transaction_id'] = transaction_id
                    context['message'] = 'Payment processed successfully!'
                else:
                    context['payment_success'] = False
                    context['message'] = 'Payment could not be completed.'
            
            except Exception as e:
                context['payment_success'] = False
                context['message'] = f'Error: {str(e)}'
        else:
            context['payment_success'] = False
            context['message'] = 'Invalid payment information.'
        
        return context


class PayPalCancelView(TemplateView):
    """
    View called if user cancels PayPal payment
    
    Usage in urls.py:
        path('paypal/cancel/', 
             PayPalCancelView.as_view(), 
             name='paypal_cancel'),
    """
    
    template_name = 'payment/paypal_cancel.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'Payment was cancelled. Please try again.'
        return context


# ============================================================================
# EXAMPLE TEMPLATES
# ============================================================================

PAYPAL_PAYMENT_FORM_TEMPLATE = """
<!-- Payment form to initiate PayPal payment -->

<div class="payment-container">
    <h2>Purchase Book</h2>
    
    <div class="book-info">
        <h3>{{ book.title }}</h3>
        <p>Price: $50.00</p>
    </div>
    
    <form method="post" action="{% url 'initiate_paypal_payment' book.id %}">
        {% csrf_token %}
        
        <button type="submit" class="btn btn-primary paypal-btn">
            🔵 Pay with PayPal
        </button>
    </form>
</div>

<style>
.payment-container {
    max-width: 400px;
    margin: 50px auto;
    padding: 30px;
    border: 1px solid #ddd;
    border-radius: 8px;
    text-align: center;
}

.book-info {
    margin: 20px 0;
}

.paypal-btn {
    background-color: #003087;
    color: white;
    padding: 12px 30px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    width: 100%;
}

.paypal-btn:hover {
    background-color: #001a4d;
}
</style>
"""

PAYPAL_SUCCESS_TEMPLATE = """
<!-- Success page after payment -->

<div class="payment-result success">
    <h1>✅ Payment Successful!</h1>
    
    {% if transaction_id %}
        <p>Transaction ID: <code>{{ transaction_id }}</code></p>
    {% endif %}
    
    <p>{{ message }}</p>
    
    <p>You now have access to the book!</p>
    
    <a href="{% url 'book_library' %}" class="btn btn-primary">
        Back to Library
    </a>
</div>

<style>
.payment-result {
    max-width: 500px;
    margin: 50px auto;
    padding: 40px;
    border-radius: 8px;
    text-align: center;
}

.payment-result.success {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
}

.payment-result code {
    background-color: rgba(0,0,0,0.1);
    padding: 5px 10px;
    border-radius: 4px;
    font-family: monospace;
}

.btn {
    display: inline-block;
    padding: 10px 20px;
    margin-top: 20px;
    border-radius: 4px;
    text-decoration: none;
}

.btn-primary {
    background-color: #007bff;
    color: white;
}

.btn-primary:hover {
    background-color: #0056b3;
}
</style>
"""

PAYPAL_CANCEL_TEMPLATE = """
<!-- Cancel page if user cancels payment -->

<div class="payment-result cancel">
    <h1>⚠️ Payment Cancelled</h1>
    
    <p>{{ message }}</p>
    
    <a href="{% url 'initiate_paypal_payment' book.id %}" class="btn btn-primary">
        Try Again
    </a>
    
    <a href="{% url 'book_library' %}" class="btn btn-secondary">
        Back to Library
    </a>
</div>

<style>
.payment-result {
    max-width: 500px;
    margin: 50px auto;
    padding: 40px;
    border-radius: 8px;
    text-align: center;
}

.payment-result.cancel {
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
}

.btn {
    display: inline-block;
    padding: 10px 20px;
    margin: 10px 5px;
    border-radius: 4px;
    text-decoration: none;
}

.btn-primary {
    background-color: #007bff;
    color: white;
}

.btn-primary:hover {
    background-color: #0056b3;
}

.btn-secondary {
    background-color: #6c757d;
    color: white;
}

.btn-secondary:hover {
    background-color: #545b62;
}
</style>
"""

# ============================================================================
# URL CONFIGURATION EXAMPLE
# ============================================================================

# Add to your urls.py:

URLS_EXAMPLE = """
# In your Django urls.py:

from django.urls import path, include
from catalogue.payment_views import (
    InitiatePayPalPaymentView,
    PayPalSuccessView,
    PayPalCancelView,
)

urlpatterns = [
    # ... other URL patterns ...
    
    # Include webhook URLs
    path('', include('catalogue.payment_paypal_urls')),
    
    # PayPal payment endpoints
    path('purchase/<int:book_id>/paypal/', 
         InitiatePayPalPaymentView.as_view(), 
         name='initiate_paypal_payment'),
    
    path('paypal/success/', 
         PayPalSuccessView.as_view(), 
         name='paypal_success'),
    
    path('paypal/cancel/', 
         PayPalCancelView.as_view(), 
         name='paypal_cancel'),
]
"""

# ============================================================================
# ENVIRONMENT VARIABLES REQUIRED
# ============================================================================

"""
Add these to your .env file:

# PayPal Sandbox Configuration (for testing)
PAYPAL_CLIENT_ID=your_sandbox_client_id_here
PAYPAL_CLIENT_SECRET=your_sandbox_client_secret_here
PAYPAL_MODE=sandbox
PAYPAL_API_URL=https://api-m.sandbox.paypal.com

# For production (change when going live)
# PAYPAL_MODE=live
# PAYPAL_CLIENT_ID=your_live_client_id_here
# PAYPAL_CLIENT_SECRET=your_live_client_secret_here
# PAYPAL_API_URL=https://api-m.paypal.com
"""

# ============================================================================
# INSTALLATION REQUIREMENTS
# ============================================================================

"""
Install required package:
    pip install paypalrestsdk

Or add to requirements.txt:
    paypalrestsdk
"""
