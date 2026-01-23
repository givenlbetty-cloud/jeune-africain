# 🚀 Moneroo Payment Integration - Lead Developer Guide

## Overview

This is a **clean, production-ready** implementation of Moneroo payment aggregator for BNC RDC.

**What Moneroo covers:**
- Mobile Money: M-Pesa, Orange Money, Airtel Money
- Cards: Visa, Mastercard
- All RDC payment methods in ONE integration

**What we've removed:**
- ❌ All old Moneiro code
- ❌ Direct USSD/STK implementations
- ❌ Manual operator-specific logic
- ❌ Legacy webhook handlers

---

## Setup (5 min)

### 1. Add to `.env`

```env
# Moneroo Payment Gateway
MONEROO_PUBLIC_KEY=your_public_key_here
MONEROO_SECRET_KEY=your_secret_key_here
```

**Get credentials from:** https://dashboard.moneroo.io/

### 2. Include URLs in main `urls.py`

```python
from django.urls import path, include

urlpatterns = [
    # ... other URLs ...
    path('', include('catalogue.urls_moneroo')),
]
```

### 3. Ensure Order model exists

The code expects:
```python
class Order(models.Model):
    user = ForeignKey(User)
    reference = CharField(unique=True)
    amount = DecimalField
    currency = CharField  # 'USD' or 'CDF'
    payment_method = CharField  # 'mobile_money' or 'card'
    book = ForeignKey(Book, null=True)
    status = CharField  # 'PENDING', 'COMPLETED', 'FAILED'
    is_paid = BooleanField(default=False)
    transaction_id = CharField(blank=True)
```

---

## Usage

### Step 1: Create Payment Form

```html
<form method="POST" action="/payment/initiate/">
    {% csrf_token %}
    
    <input type="hidden" name="amount" value="100.00">
    <input type="hidden" name="currency" value="USD">
    <input type="hidden" name="reference" value="ORDER-{{ timestamp }}">
    <input type="hidden" name="book_id" value="{{ book.id }}">
    
    <select name="payment_method" required>
        <option value="mobile_money">📱 Mobile Money (M-Pesa, Orange, Airtel)</option>
        <option value="card">💳 Credit/Debit Card (Visa, Mastercard)</option>
    </select>
    
    <input type="tel" name="phone" placeholder="+243..." required>
    
    <button type="submit">Proceed to Payment</button>
</form>
```

### Step 2: User Flow

```
1. User selects payment method
   ↓
2. POST /payment/initiate/
   ↓
3. Django creates Order (PENDING)
   ↓
4. Calls Moneroo API
   ↓
5. Redirects to Moneroo payment page
   ↓
6. User completes payment
   ↓
7. Moneroo sends webhook POST /payment/moneroo-callback/
   ↓
8. Webhook validates signature
   ↓
9. Updates Order (COMPLETED)
   ↓
10. Grants book access
    ↓
11. Sends confirmation email
```

---

## Code Structure

### `views_moneroo.py`

**Functions:**

1. **`initiate_moneroo_payment(request)`**
   - POST endpoint
   - Creates order in DB
   - Calls Moneroo API
   - Redirects to payment page

2. **`moneroo_callback(request)`**
   - Webhook handler (@csrf_exempt)
   - Validates signature (HMAC-SHA256)
   - Updates order status
   - Grants book access
   - Sends email

3. **Helper functions**
   - `_handle_payment_success()`: Update order, grant access
   - `_handle_payment_failure()`: Mark as failed
   - `_generate_signature()`: HMAC-SHA256
   - `_verify_signature()`: Constant-time comparison
   - `_send_confirmation_email()`: Email on success
   - `_send_failure_email()`: Email on failure

### `urls_moneroo.py`

Routes:
- `POST /payment/initiate/` → `initiate_moneroo_payment`
- `POST /payment/moneroo-callback/` → `moneroo_callback`
- `GET /payment/callback/` → `payment_callback`

---

## Security

✅ **Signature Validation**
- All webhooks validated with HMAC-SHA256
- Uses `hmac.compare_digest()` to prevent timing attacks
- Constant-time comparison

✅ **Credentials Management**
- Keys stored in `.env` only
- Accessed via `os.getenv()`
- Never hardcoded

✅ **CSRF**
- Webhook endpoint uses `@csrf_exempt` (necessary for external service)
- All user-facing endpoints protected

✅ **Error Handling**
- Try/except on all API calls
- Graceful fallbacks
- Comprehensive logging

---

## Moneroo API Reference

### Initialize Payment

```
POST https://api.moneroo.io/v1/payments/initialize

Headers:
  Content-Type: application/json
  Authorization: Bearer {MONEROO_PUBLIC_KEY}

Body:
{
  "public_key": "string",
  "amount": 100.00,
  "currency": "USD",
  "customer_email": "user@example.com",
  "customer_phone": "+243123456789",
  "order_id": "ORDER-123",
  "payment_method": "mobile_money|card",
  "return_url": "https://domain.com/payment/callback/",
  "callback_url": "https://domain.com/payment/moneroo-callback/"
}

Response:
{
  "data": {
    "payment_url": "https://pay.moneroo.io/...",
    "payment_id": "PAY-xxx"
  }
}
```

### Webhook Payload

```
POST {callback_url}

{
  "event": "payment.completed",
  "data": {
    "order_id": "ORDER-123",
    "amount": 100.00,
    "currency": "USD",
    "status": "completed",
    "transaction_id": "TXN-xxx",
    "payment_method": "mobile_money",
    "signature": "hmac_signature"
  }
}
```

---

## Testing

### Test Credentials

```env
MONEROO_PUBLIC_KEY=pk_test_...
MONEROO_SECRET_KEY=sk_test_...
```

### Test Payment Methods

- **M-Pesa:** +254712345678
- **Orange Money:** +243812345678
- **Airtel Money:** +243812345678
- **Cards:** Use Moneroo test card numbers

### Test Webhook

```bash
curl -X POST http://localhost:8000/payment/moneroo-callback/ \
  -H "Content-Type: application/json" \
  -d '{
    "event": "payment.completed",
    "data": {
      "order_id": "ORDER-TEST-123",
      "amount": 100.00,
      "currency": "USD",
      "status": "completed",
      "transaction_id": "TXN-TEST-123",
      "payment_method": "mobile_money"
    }
  }'
```

---

## Troubleshooting

### "MONEROO_PUBLIC_KEY not set"

**Fix:**
```env
MONEROO_PUBLIC_KEY=pk_test_xxxxx
MONEROO_SECRET_KEY=sk_test_xxxxx
```

Then restart Django:
```bash
python manage.py runserver
```

### "Payment URL not returned"

**Cause:** API response format mismatch
**Fix:** Check Moneroo API documentation for current response format

### "Invalid signature"

**Cause:** Secret key mismatch
**Fix:** Verify `MONEROO_SECRET_KEY` matches Moneroo dashboard

### "Order not found"

**Cause:** Order reference doesn't match webhook data
**Fix:** Ensure `order_id` in webhook matches `reference` field in database

---

## Production Checklist

- [ ] Moneroo credentials configured in `.env`
- [ ] URLs included in main `urls.py`
- [ ] Order model has required fields
- [ ] Email SMTP configured (for confirmations)
- [ ] Webhook URL configured in Moneroo dashboard
- [ ] HTTPS enabled
- [ ] `DEBUG=False` in production
- [ ] Logging configured
- [ ] Database backups enabled

---

## Files

- ✅ `views_moneroo.py` - Payment views and webhook handler
- ✅ `urls_moneroo.py` - URL routing
- ✅ Documentation (this file)

---

## Support

For Moneroo API issues:
- https://moneroo.io
- https://docs.moneroo.io
- support@moneroo.io

For BNC integration support:
- Check logs: `python manage.py shell` → `import logging; logger = logging.getLogger('__name__')`
- Enable DEBUG mode for detailed error messages

---

**Status:** ✅ Production Ready
**Last Updated:** December 28, 2025
