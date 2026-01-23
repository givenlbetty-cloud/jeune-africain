# 💳 Intégration Moneiro - Guide Complet

## Vue d'ensemble

Ce projet intègre l'API Moneiro pour accepter les paiements mobiles en RDC:
- **M-Pesa** (Kenya & Afrique)
- **Orange Money** (Afrique Centrale)
- **Airtel Money** (Afrique de l'Ouest)

## Installation

### 1. Installer les dépendances

```bash
pip install requests
```

### 2. Configurer les variables d'environnement

Ajoute à ton fichier `.env`:

```env
# Moneiro Payment Configuration
MONEIRO_API_KEY=your_api_key_here
MONEIRO_API_SECRET=your_api_secret_here
MONEIRO_MERCHANT_ID=your_merchant_id_here
MONEIRO_API_URL=https://api.moneiro.com/v1
```

### 3. Intégrer les URLs

Dans `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # Autres URLs...
    path('', include('catalogue.payment_moneiro_urls')),
]
```

## Utilisation

### Initiating a Payment

```python
from decimal import Decimal
from catalogue.payment_moneiro import commander_paiement

# Initiate payment
success, payment_url, transaction_id = commander_paiement(
    amount=Decimal('100.00'),
    currency='USD',
    customer_email='user@example.com',
    customer_phone='+243123456789',
    description='Book purchase',
    payment_method='mpesa',  # or 'orange_money', 'airtel_money'
    success_url='https://yourdomain.com/success/',
    cancel_url='https://yourdomain.com/cancel/',
    order_id='ORDER-12345',
)

if success:
    # Redirect user to payment page
    return redirect(payment_url)
else:
    # Handle error
    return JsonResponse({'error': 'Payment failed'}, status=500)
```

### Supported Payment Methods

```python
from catalogue.payment_moneiro import MoneirPaymentClient

# Get available payment methods
methods = MoneirPaymentClient.get_payment_methods()
# {'mpesa': 'M-Pesa', 'orange_money': 'Orange Money', 'airtel_money': 'Airtel Money'}

# Get supported currencies
currencies = MoneirPaymentClient.get_currencies()
# {'CDF': 'Congolese Franc', 'USD': 'US Dollar'}
```

## Architecture

### Files

1. **payment_moneiro.py**
   - `MoneirPaymentClient`: Main class for API interaction
   - `commander_paiement()`: Convenience function to initiate payments

2. **payment_moneiro_webhook.py**
   - `moneiro_webhook()`: Webhook endpoint for payment confirmations
   - Payment status handlers: success, failure, pending

3. **payment_moneiro_urls.py**
   - URL routing for webhook endpoint

4. **payment_moneiro_examples.py**
   - Usage examples in views
   - Template examples
   - Integration guidance

## Payment Flow

```
1. User selects book and payment method
        ↓
2. Django creates Order (PENDING status)
        ↓
3. commander_paiement() initiates payment with Moneiro
        ↓
4. User is redirected to Moneiro payment page
        ↓
5. User completes payment on Moneiro (or cancels)
        ↓
6. Moneiro sends webhook to /api/webhooks/moneiro/
        ↓
7. Webhook handler validates signature and updates Order status
        ↓
8. User is granted access to book (if payment succeeded)
        ↓
9. Confirmation email is sent to user
```

## Webhook Configuration

### In Moneiro Dashboard

1. Go to Webhooks settings
2. Add endpoint: `https://yourdomain.com/api/webhooks/moneiro/`
3. Enable events:
   - `payment.completed`
   - `payment.failed`
   - `payment.pending`

### Signature Validation

Moneiro signs all webhooks with HMAC-SHA256. The signature is validated automatically in `moneiro_webhook()`.

## Error Handling

### API Errors

```python
success, payment_url, tx_id = commander_paiement(...)

if not success:
    logger.error(f"Payment failed: {order_id}")
    # Handle error (show message to user, etc.)
```

### Webhook Errors

- **Invalid Signature**: Returns 401, webhook rejected
- **Invalid JSON**: Returns 400, webhook rejected
- **Processing Error**: Returns 500, webhook acknowledged but may need retry

## Testing

### Test Payment Methods

Use Moneiro's test credentials in sandbox environment:

```python
# In settings.py or .env (for testing)
MONEIRO_API_URL=https://sandbox.moneiro.com/v1  # Use sandbox for testing
```

### Test Transactions

Use these test phone numbers (in sandbox):

- M-Pesa: `+254712345678`
- Orange Money: `+243812345678`
- Airtel Money: `+243812345678`

## Security Considerations

1. **API Keys**: Store in `.env`, never commit
2. **CSRF Exempt**: Webhook endpoint is exempt (signature validation instead)
3. **HTTPS Only**: Use HTTPS in production
4. **Signature Validation**: All webhooks are validated
5. **Rate Limiting**: Consider adding rate limiting to webhook endpoint

## Logging

All payment operations are logged:

```python
logger.info(f"Payment initiated: {order_id}, Amount: {amount} {currency}")
logger.error(f"Payment failed: {error}")
logger.info(f"Webhook received: TxID={transaction_id}, Status={status}")
```

Access logs in Django logs or monitoring system.

## Troubleshooting

### "API credentials not configured"

```python
# Solution: Add to .env
MONEIRO_API_KEY=your_key
MONEIRO_API_SECRET=your_secret
MONEIRO_MERCHANT_ID=your_id
```

### "Invalid webhook signature"

```python
# Solution: Ensure API_SECRET is correct and matches in Moneiro dashboard
# Webhook signature is HMAC-SHA256 of payload with API_SECRET as key
```

### "Order not found" in webhook

```python
# Solution: Ensure order_id in webhook matches Order.id in database
# Check that order_id is unique and correctly passed to payment initiation
```

## Support

For Moneiro API issues:
- https://moneiro.com
- https://docs.moneiro.com
- support@moneiro.com

## License

This integration is part of the BNC Digital Library project.
