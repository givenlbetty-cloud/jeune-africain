# 🚀 QUICK START GUIDE - New Developer Onboarding

## Welcome to BNC Library Management System

You've joined the project on December 21, 2025. Three major features have just been implemented. Here's what you need to know:

---

## 📊 WHAT WAS JUST BUILT (21 DEC 2025)

### 1. **Payment System** (Mobile Money)
Users can now purchase books using:
- 🇺🇬 Airtel Money (Uganda)
- 🇰🇪 M-Pesa (Kenya) 
- 🇨🇩 Orange Money RDC (Congo)

**Files:** `catalogue/payment_gateways.py`, `catalogue/payment_views.py`
**Docs:** `MOBILE_MONEY_PAYMENT_DOCUMENTATION.md`

### 2. **Free Preview System**
Readers can preview first 12-30 pages of paid books before buying.

**Files:** `catalogue/preview_views.py`
**Docs:** `FREE_PREVIEW_DOCUMENTATION.md`

### 3. **Events & Announcements**
Admins can create events/workshops/conferences. Users can register.

**Files:** `catalogue/models.py` (EventRegistration), `catalogue/events_views.py`, `catalogue/admin.py`
**Docs:** `VERIFICATION_CHECKLIST.md`

---

## 🎯 DEVELOPER WORKFLOWS

### Deploy These Features

```bash
# 1. Pull latest code (already done, migrations applied)
git pull origin main

# 2. Check system health
python manage.py check

# 3. Run local server
python manage.py runserver 0.0.0.0:8000

# 4. Test endpoints
bash test_integration.sh

# 5. View in admin
# Go to http://localhost:8000/admin/
# → Catalogue → Events or Event Registrations
```

### Add New Payment Provider

**Example: Adding Flutterwave**

1. Create gateway class in `payment_gateways.py`:
```python
class FlutterwaveGateway(PaymentGateway):
    def __init__(self, payment):
        self.payment = payment
    
    def get_access_token(self):
        # Use Flutterwave API key
        pass
    
    def initiate_payment(self):
        # Call Flutterwave endpoint
        pass
    
    def verify_payment(self):
        # Poll or wait for webhook
        pass
```

2. Update `get_payment_gateway()` in same file:
```python
def get_payment_gateway(payment):
    # ... existing code ...
    elif payment.mobile_money_provider == 'FLUTTERWAVE':
        return FlutterwaveGateway(payment)
```

3. Add webhook in `payment_views.py`:
```python
@csrf_exempt
def flutterwave_webhook(request):
    # Parse callback, update Payment status
    pass
```

4. Add URL in `urls.py`:
```python
path('api/payments/webhook/flutterwave/', flutterwave_webhook)
```

### Modify Free Preview Logic

The limit is set in Django Admin. To change:

1. Go to `/admin/catalogue/book/`
2. Edit any book
3. Set "Free Pages Count" (0 = free, 1-30 = preview pages)

To change the access control logic:
1. Edit `catalogue/preview_views.py`
2. Look for `can_read_full_book_view()` function
3. Modify the logic (e.g., time-limited previews)
4. No migration needed

### Create/Manage Events

**Via Admin Panel:**
1. Go to `/admin/catalogue/event/`
2. Click "Add Event"
3. Fill: title, description, type, dates, location
4. Click "Save"

**Check Registrations:**
1. Go to `/admin/catalogue/eventregistration/`
2. See all user registrations
3. Mark "Attended" for real attendees

**Via API (Programmatic):**
```python
from catalogue.models import Event, EventRegistration
from django.utils import timezone

# Create event
event = Event.objects.create(
    title="Tech Workshop",
    event_type="WORKSHOP",
    date_start=timezone.now() + timedelta(days=7),
    location="Room 101"
)

# Check registrations
count = event.registrations.count()
attendees = event.registrations.filter(attended=True)
```

---

## 📁 KEY FILES TO KNOW

### Models
- `catalogue/models.py` - Event (pre-existing), EventRegistration (new)

### Views & Logic
- `catalogue/payment_gateways.py` - 3 payment providers (Airtel, M-Pesa, Orange)
- `catalogue/payment_views.py` - Payment endpoints + webhooks
- `catalogue/preview_views.py` - Free preview access control
- `catalogue/events_views.py` - Event listing, registration, statistics
- `catalogue/frontend_views.py` - Event detail view (pre-existing)

### URLs
- `catalogue/urls.py` - All routes (14 new endpoints)

### Admin
- `catalogue/admin.py` - EventRegistrationAdmin (new)

### Database
- `catalogue/migrations/0015_*.py` - Payment Mobile Money fields
- `catalogue/migrations/0016_*.py` - EventRegistration model

### Documentation
- `MOBILE_MONEY_PAYMENT_DOCUMENTATION.md` - Payment setup & examples
- `FREE_PREVIEW_DOCUMENTATION.md` - Preview system guide
- `VERIFICATION_CHECKLIST.md` - What's been verified
- `TECHNICAL_IMPLEMENTATION.md` - Technical deep dive

---

## 🧪 TESTING

### Run All Tests
```bash
bash test_integration.sh
```

### Test Single Endpoint
```bash
# Get list of events
curl http://localhost:8000/api/events/

# Get specific event
curl http://localhost:8000/api/events/{event_id}/

# Check if you can read a book
curl http://localhost:8000/api/book/{book_id}/can-read/

# Check page access
curl http://localhost:8000/api/book/{book_id}/page/10/access/
```

### Test in Django Shell
```bash
python manage.py shell

# Import models
from catalogue.models import Event, EventRegistration, Payment
from catalogue.events_views import events_list_api_view

# Test queries
Event.objects.filter(is_published=True).count()
EventRegistration.objects.select_related('event').first()
Payment.objects.filter(status='COMPLETED').count()
```

---

## 🔐 SECURITY NOTES

### Payment Webhooks
- Endpoints are `/api/payments/webhook/{provider}/`
- They have `@csrf_exempt` (providers don't send CSRF tokens)
- Always validate webhook signature/origin in production
- Store webhook_data JSONB for audit trail

### Free Preview
- Page limits enforced SERVER-SIDE, not client-side
- Always call `/api/book/{id}/page/{num}/access/` before rendering
- Never trust client-side JavaScript to enforce limits

### Events
- Authentication required for registration/unregistration
- Use `@login_required` decorator on registration views
- Prevent duplicate registrations with unique_together constraint

---

## 📈 NEXT PRIORITIES

### Short Term (1-2 weeks)
1. **Frontend UI** - Build payment, preview, event registration UIs
2. **Testing** - Integration tests with real payment providers
3. **Deployment** - Set up production environment

### Medium Term (1 month)
1. **Admin Dashboard** - Add charts/stats widgets
2. **Notifications** - Email on payment/registration confirmation
3. **Analytics** - Track conversion, engagement metrics

### Long Term (3+ months)
1. **Refunds** - Payment refund system
2. **Time-Limited Preview** - Expire previews after X days
3. **Recommendation Engine** - Suggest books based on history

---

## 🐛 IF YOU FIND BUGS

1. **Check** `VERIFICATION_CHECKLIST.md` - Known-good status
2. **Look at** `test_integration.sh` - How to test
3. **Review** code comments - Lots of documentation
4. **Search** issue tracker for similar problems
5. **Ask** senior developer before making changes

---

## 💬 COMMON QUESTIONS

**Q: Where do I add a new payment provider?**
A: `catalogue/payment_gateways.py` - Create new gateway class, update `get_payment_gateway()`

**Q: How do I change preview page count?**
A: Django Admin → Book edit → "Free Pages Count" field

**Q: Where are the API docs?**
A: `MOBILE_MONEY_PAYMENT_DOCUMENTATION.md`, `FREE_PREVIEW_DOCUMENTATION.md`, `API_DOCUMENTATION.md`

**Q: Why is EventRegistration needed?**
A: Track which users registered for which events (for attendance, notifications, analytics)

**Q: Can users preview books they purchased?**
A: Yes, they get full access (can_read_full=True)

**Q: Are webhooks tested with real providers?**
A: Not yet - use sandbox credentials for testing

---

## ✅ BEFORE YOU START CODING

1. Read `TECHNICAL_IMPLEMENTATION.md` - Understand the architecture
2. Check `VERIFICATION_CHECKLIST.md` - What's working
3. Run `test_integration.sh` - Verify local setup
4. Review relevant docs (payment/preview/events)
5. Understand the 3 systems: payment → preview (integration) → events (independent)

---

## 🎯 SUCCESS CRITERIA

Your changes are good if:
- ✅ `python manage.py check` passes (0 errors)
- ✅ All migrations applied
- ✅ Django admin works for your changes
- ✅ API endpoints return correct JSON
- ✅ Tests pass: `bash test_integration.sh`

---

## 🤝 GET HELP

**For Payment System:**
→ See `MOBILE_MONEY_PAYMENT_DOCUMENTATION.md`

**For Free Preview:**
→ See `FREE_PREVIEW_DOCUMENTATION.md`

**For Events:**
→ Check `catalogue/admin.py` and `catalogue/events_views.py`

**For General Questions:**
→ Check code comments and docstrings (well-documented!)

---

**Welcome aboard! 🚀**

Understand the architecture → Test locally → Make changes → Test again → Deploy with confidence.

**Session Date:** December 21, 2025
**Project Status:** 85%+ Complete
**Frontend UI:** Next priority
