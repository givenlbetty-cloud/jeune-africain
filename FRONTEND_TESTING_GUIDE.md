# 🧪 Frontend UI Testing Guide

## Quick Start Testing

### Test Environment Setup
```bash
# Terminal 1: Start Django server
python manage.py runserver 0.0.0.0:8000

# Terminal 2: Check server is running
curl http://localhost:8000/api/events/
```

---

## Test 1: Payment Modal

### Prerequisites
- User account (create one if needed)
- Book with `is_paid=True`

### Steps
1. **Navigate to book detail page**
   ```
   URL: http://localhost:8000/catalogue/book/<book_id>/
   ```

2. **Verify payment button appears**
   - If not purchased: "Acheter" button visible
   - If purchased: "Lire le livre" button visible

3. **Click "Acheter" button**
   - ✅ Payment modal should open (no page reload)
   - ✅ Modal should show payment provider selection

4. **Select payment provider**
   - Click dropdown: should show 3 options
   - Airtel Money (🇺🇬 +256)
   - M-Pesa (🇰🇪 +254)
   - Orange Money RDC (🇨🇩 +243)

5. **Check phone prefix changes**
   - Select "Airtel Money" → prefix becomes "+256"
   - Select "M-Pesa" → prefix becomes "+254"
   - Select "Orange Money RDC" → prefix becomes "+243"

6. **Enter phone number**
   - Type "123456789" (9 digits)
   - Should display as "+256 123456789" (for Airtel)
   - Field should show validation message if invalid

7. **Accept terms**
   - Check "I accept terms" checkbox
   - Button should become enabled

8. **Submit payment**
   - Click "Procéder au paiement"
   - ✅ Status modal should appear
   - ✅ Spinner animation should show
   - ✅ Message: "Confirmer sur votre téléphone"

9. **Monitor polling**
   - Check browser console (F12)
   - Should see: "Checking payment status..."
   - Checks every 2 seconds

10. **Handle timeout**
    - If no response after 2 minutes
    - ✅ Modal should show: "Délai d'attente dépassé"
    - ✅ "Réessayer" button appears

**Success Criteria:** ✅
- [ ] Modal opens without page reload
- [ ] Provider dropdown works
- [ ] Phone prefix updates
- [ ] Phone validation works
- [ ] Terms checkbox required
- [ ] Status modal shows
- [ ] No console errors

---

## Test 2: Preview Banner

### Prerequisites
- Free book with `free_pages_count = 20` (or any number 1-30)
- User NOT logged in or NOT purchased book
- Book must have PDF

### Steps
1. **Open book reader**
   ```
   URL: http://localhost:8000/catalogue/book/<book_id>/read/
   ```

2. **Verify preview banner appears**
   - ✅ Banner should show: "📖 Prévisualisation Gratuite"
   - ✅ Should show: "Vous lisez la 1 sur 20 pages"
   - ✅ Progress bar visible (0%)
   - ✅ "💳 Acheter le livre" button visible

3. **Read through pages**
   - Scroll through pages 1-10
   - ✅ Progress bar should update
   - ✅ Page number should update: "Vous lisez la 10 sur 20"

4. **Continue scrolling**
   - Scroll to page 20
   - ✅ Progress bar near 100% (almost full)
   - ✅ Page number shows: "20 sur 20"

5. **Try to access page 21**
   - Scroll past page 20
   - ✅ Modal should appear: "Limite de prévisualisation atteinte"
   - ✅ Should show: "Vous avez lu 20 pages sur 384"
   - ✅ Shows preview percentage: "5% du livre"
   - ✅ Book details shown (pages, price)

6. **Test "Buy Now" button in modal**
   - Click "💳 Acheter maintenant"
   - ✅ Payment modal should open
   - ✅ Preview modal should close
   - (Same as Test 1: Payment Modal)

7. **Simulate successful payment** (in database)
   - Create Payment with `status='COMPLETED'`
   - Reload page
   - ✅ Preview banner should disappear
   - ✅ All pages should be accessible

**Success Criteria:** ✅
- [ ] Banner appears for free users
- [ ] Progress bar updates
- [ ] Page number updates
- [ ] Modal appears at limit
- [ ] Statistics displayed
- [ ] "Buy Now" works
- [ ] No console errors

---

## Test 3: Events Search & Filter

### Prerequisites
- At least 5 events in database
- Multiple event types (NEW_BOOK, WORKSHOP, CONFERENCE, etc.)

### Steps
1. **Navigate to events page**
   ```
   URL: http://localhost:8000/catalogue/events/
   ```

2. **Verify events load**
   - ✅ Events page shows
   - ✅ Events listed in cards
   - ✅ Shows upcoming/happening/past sections

3. **Test search**
   - Type "Django" in search box
   - ✅ Results filter in real-time
   - ✅ Shows only matching events
   - Clear search (empty box)
   - ✅ All events reappear

4. **Test type filter**
   - Click "📕 Nouveaux Livres" button
   - ✅ Only NEW_BOOK events show
   - Click "🎓 Ateliers"
   - ✅ Only WORKSHOP events show
   - Click "📅 Tous"
   - ✅ All events show again

5. **Verify event status organization**
   - Upcoming events: in first section (start_date > now)
   - Happening now: in second section (start_date <= now <= end_date)
   - Past events: in third section (end_date < now)
   - ✅ Live indicator shows "EN DIRECT" for happening events

6. **Check event cards**
   - Icon matches type (📕 📍 🎓 🎤 📢)
   - Title displayed
   - Description truncated (100 chars)
   - Date/time formatted
   - Location shown
   - Registration count shown

**Success Criteria:** ✅
- [ ] Events page loads
- [ ] Search filters in real-time
- [ ] Type filter works (5 buttons)
- [ ] Status sections correct
- [ ] Live indicator visible
- [ ] Cards display all info
- [ ] No console errors

---

## Test 4: Event Registration Modal

### Prerequisites
- User logged in
- Event in database (e.g., NEW_BOOK type)
- User NOT registered for event

### Steps
1. **Open events page** (from Test 3)
   ```
   URL: http://localhost:8000/catalogue/events/
   ```

2. **Click event card's "Détails" button**
   - ✅ Events modal should open
   - ✅ Modal title: "📅 S'inscrire à cet événement"

3. **Verify event details displayed**
   - ✅ Event type badge shown with icon
   - ✅ Event title shown
   - ✅ Event description shown
   - ✅ Registration count shown (e.g., "5 / 100")
   - ✅ Event status shown (upcoming/happening/past)
   - ✅ Date and time formatted correctly
   - ✅ Location displayed

4. **Check registration status**
   - Should show: "Vous n'êtes pas inscrit"
   - Button should say: "✓ S'inscrire"
   - Button color: primary (blue)

5. **Check terms checkbox**
   - Checkbox visible
   - Label: "Je confirme mon inscription..."
   - Unchecked by default

6. **Click register button**
   - ✅ API call made: POST /api/events/<event_id>/register/
   - ✅ Success message appears
   - ✅ Button changes to: "✗ Se désinscrire"
   - ✅ Button color changes: danger (red)
   - ✅ Status shows: "Vous êtes déjà inscrit"

7. **Unregister**
   - Click "Se désinscrire" button
   - ✅ API call made: DELETE /api/events/<event_id>/unregister/
   - ✅ Success message appears
   - ✅ Button changes back to: "S'inscrire"
   - ✅ Status message disappears

8. **Test multiple registrations**
   - Register for event
   - Close modal
   - Reopen modal (click Details again)
   - ✅ Should show: "Vous êtes déjà inscrit"
   - ✅ Button shows: "Se désinscrire"

**Success Criteria:** ✅
- [ ] Modal opens without full page load
- [ ] Event details display correctly
- [ ] Registration status accurate
- [ ] Register button works (POST)
- [ ] Unregister button works (DELETE)
- [ ] Success messages show
- [ ] Button states update
- [ ] Multiple calls work correctly
- [ ] No console errors

---

## Test 5: End-to-End Payment Flow

### Complete flow from book purchase to access

### Prerequisites
- Book with `free_pages_count=0` (paid only)
- User account (not purchased)
- Book has readable PDF

### Steps
1. **Start at book detail**
   ```
   URL: http://localhost:8000/catalogue/book/<book_id>/
   ```

2. **Initiate purchase**
   - Click "Acheter" button
   - ✅ Payment modal opens

3. **Fill payment form**
   - Select provider: "M-Pesa"
   - Phone: "712345678"
   - Check terms
   - Click "Procéder au paiement"

4. **Monitor API calls**
   - Network tab (F12)
   - ✅ POST to `/api/payments/mobile-money/<book_id>/initiate/`
   - ✅ Response: `{"success": true, "payment_id": "..."}`

5. **Status polling**
   - Status modal shows
   - Check Network tab
   - ✅ GET to `/api/payments/mobile-money/<payment_id>/status/`
   - Repeats every 2 seconds

6. **Simulate payment completion**
   - In Django admin or database
   - Update Payment: `status='COMPLETED'`
   - Within 2 seconds, modal updates
   - ✅ Shows: "✓ Paiement réussi"
   - ✅ Shows: "Accès au livre activé"

7. **Page reload**
   - ✅ Modal automatically closes
   - ✅ Page reloads (book_detail)
   - ✅ "Lire le livre" button now visible
   - "Acheter" button disappeared

8. **Access book**
   - Click "Lire le livre"
   - ✅ Opens book reader

9. **Verify access**
   - Book reader opens
   - ✅ No preview banner
   - ✅ All pages accessible

**Success Criteria:** ✅
- [ ] Payment modal opens
- [ ] API initiates payment correctly
- [ ] Polling starts and checks status
- [ ] Modal updates on payment success
- [ ] Page reloads after success
- [ ] Button states change
- [ ] Book reader opens
- [ ] Full access granted

---

## Browser Console Testing

### Check for errors
Open Developer Tools (F12) and check Console tab

**Expected:** No red errors
```javascript
// Should NOT see:
❌ Uncaught TypeError
❌ 404 Not Found
❌ CORS error
❌ Uncaught SyntaxError

// Should see normal logs:
✅ API calls to /api/payments/...
✅ API calls to /api/events/...
✅ Status checking messages
✅ Component initialization logs
```

---

## Mobile Responsiveness Testing

### Test on mobile devices or dev tools

1. **Payment Modal**
   - ✅ Modal centered on screen
   - ✅ Buttons full width
   - ✅ Input fields readable
   - ✅ No horizontal scroll

2. **Preview Banner**
   - ✅ Stacks vertically
   - ✅ Button visible and clickable
   - ✅ Progress bar readable

3. **Events Cards**
   - ✅ Single column layout
   - ✅ Cards take full width
   - ✅ Text readable
   - ✅ Buttons accessible

4. **Event Modal**
   - ✅ Fits screen height
   - ✅ Scrollable if needed
   - ✅ Buttons accessible

---

## Performance Testing

### API Response Times
```bash
# Check payment API
curl -X GET http://localhost:8000/api/payments/mobile-money/1/status/ \
  -H "Authorization: Bearer <token>"

# Expected response time: < 200ms
```

### Search Performance
1. Open events page
2. Type quickly in search box
3. ✅ Should NOT make API call per keystroke
4. ✅ Should debounce (300ms default)
5. ✅ Should only make 1-2 API calls total

---

## Error Handling Testing

### Network Error Simulation
1. Open DevTools Network tab
2. Select "Throttling: Offline"
3. Try payment → ✅ Should show error message
4. Try search → ✅ Should show error gracefully
5. Turn throttling off → Try again → ✅ Should recover

### Invalid Input
1. Payment modal: Enter invalid phone
   - ✅ Should show validation error
   - ✅ Submit button disabled

2. Events: Try unauth register
   - ✅ Should redirect to login
   - Or ✅ Show error message

---

## Testing Checklist

### UI/UX
- [ ] All modals open without page reload
- [ ] All buttons have proper hover states
- [ ] Colors match design system
- [ ] Text is readable on all backgrounds
- [ ] No layout shifts or jumps
- [ ] Loading spinners animate smoothly
- [ ] Success/error messages clear

### Functionality
- [ ] Payment form validates
- [ ] API calls succeed
- [ ] Status polling works
- [ ] Preview limits enforced
- [ ] Events search filters
- [ ] Event registration toggles
- [ ] Page reloads on success

### Security
- [ ] CSRF tokens present in forms
- [ ] No sensitive data in console
- [ ] No hardcoded API keys
- [ ] Authentication required where needed
- [ ] Permissions enforced

### Browser Compatibility
- [ ] Chrome/Edge works ✅
- [ ] Firefox works ✅
- [ ] Safari works ✅
- [ ] Mobile browsers work ✅

### Accessibility
- [ ] Modals have proper focus management
- [ ] Buttons have proper aria-labels
- [ ] Form labels associated with inputs
- [ ] Color contrast sufficient
- [ ] Keyboard navigation works

---

## Troubleshooting

### "Modal doesn't open"
- **Check:** JavaScript error in console
- **Check:** Bootstrap 5.3 CSS loaded
- **Check:** Element ID matches (e.g., `payment-modal`)
- **Solution:** Clear browser cache, hard reload

### "API calls fail"
- **Check:** Server running (`python manage.py runserver`)
- **Check:** CSRF token present in request
- **Check:** User authenticated (if required)
- **Check:** API endpoint exists
- **Solution:** Check Django error logs

### "Preview banner not showing"
- **Check:** Book has `free_pages_count > 0`
- **Check:** User not already purchased
- **Check:** `initializePreviewSystem()` called
- **Solution:** Check `can-read` API response

### "Events don't load"
- **Check:** Events exist in database
- **Check:** Events `is_published=True`
- **Check:** API endpoint working
- **Solution:** Check `GET /api/events/` directly

### "Phone number validation fails"
- **Check:** Correct provider selected
- **Check:** Expected digit count for provider
  - Airtel: 9-10 digits
  - M-Pesa: 9-10 digits
  - Orange: 9-10 digits
- **Solution:** Try different phone number

---

## Summary

**All 4 components are now testable:**
1. ✅ Payment Modal (book purchase)
2. ✅ Preview Banner (free preview limits)
3. ✅ Events Modal (event registration)
4. ✅ Events Listing (event discovery)

**Total test scenarios:** 5 main flows
**Estimated testing time:** 30-45 minutes
**Success criteria:** All checks pass ✅

---

*Generated December 21, 2025 - Frontend UI Testing Guide*
