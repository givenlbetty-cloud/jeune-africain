# 🧪 MANUAL TESTING GUIDE - Analytics Dashboard

**Date:** 26 December 2025  
**Status:** ✅ SERVER RUNNING on http://localhost:8000/

---

## ✅ WHAT'S WORKING

1. **Server Running** ✅
   - Django development server started
   - No system errors detected
   - All Python files compiled successfully

2. **Analytics Views & URLs** ✅
   - Fixed all UserBookInteraction imports
   - Using correct models: ReaderActivity, BookRating, ReadingSession, LibraryBook
   - All API endpoints integrated

3. **Database Models** ✅
   - ReaderActivity (user activity tracking)
   - BookRating (book ratings/reviews)
   - ReadingSession (reading progress)
   - LibraryBook (user library)

---

## 🧪 TESTING CHECKLIST

### Phase 1: Authentication (5 min)
- [ ] Go to http://localhost:8000/fr/
- [ ] Click "Se connecter" / "Sign In"
- [ ] Login with existing account or create new one
- [ ] Verify you're logged in (profile shows in navbar)

### Phase 2: Analytics Dashboard (5 min)
- [ ] After login, look for "Analytics" link in navbar
- [ ] Click "Analytics" or go to http://localhost:8000/fr/analytics/
- [ ] Verify dashboard loads without errors
- [ ] Check stat cards appear (Books Read, Pages, Avg Rating, etc.)

### Phase 3: Chart Visualization (5 min)
- [ ] Scroll down to see charts
- [ ] Verify "Reading Trends" line chart displays
- [ ] Verify "Favorite Genres" doughnut chart displays
- [ ] Check "Monthly Goal Progress" circular indicator
- [ ] Verify "Library Overview" cards show

### Phase 4: Date Range Filtering (5 min)
- [ ] Click date range dropdown at top
- [ ] Select "Last 7 days"
- [ ] Verify charts update and data changes
- [ ] Try "Last 30 days", "Last 90 days", "Last 365 days"
- [ ] Verify data recalculates for each range

### Phase 5: API Endpoints (10 min)
Open DevTools (F12) → Network tab, then test:

**Test 1: User Statistics**
```
URL: http://localhost:8000/fr/analytics/api/stats/?days=30
Expected: JSON with books_read, total_pages, avg_rating, etc.
```

**Test 2: Reading Trends**
```
URL: http://localhost:8000/fr/analytics/api/trends/?days=30
Expected: Array of objects with date and count
```

**Test 3: Genres**
```
URL: http://localhost:8000/fr/analytics/api/genres/?limit=5
Expected: Array of genres with count
```

**Test 4: Library Stats**
```
URL: http://localhost:8000/fr/analytics/api/library/
Expected: JSON with library_books, favorite_books, wishlist_books, purchased_books
```

**Test 5: Recommendations**
```
URL: http://localhost:8000/fr/analytics/api/recommendations/?days=30
Expected: JSON with recommendation_clicks, purchases, conversion_rate
```

**Test 6: Reading Pace**
```
URL: http://localhost:8000/fr/analytics/api/reading-pace/?days=30
Expected: JSON with reading_pace, interactions_count, days_analyzed
```

**Test 7: Monthly Comparison**
```
URL: http://localhost:8000/fr/analytics/api/monthly-comparison/
Expected: JSON with current_month, previous_month, growth_percentage
```

### Phase 6: Responsive Design (5 min)
- [ ] Press F12 (DevTools)
- [ ] Click "Toggle Device Toolbar" 
- [ ] Test on "iPhone SE" (mobile)
- [ ] Verify cards stack vertically
- [ ] Test on "iPad" (tablet)
- [ ] Verify 2-column layout
- [ ] Test on desktop (4-column layout)

### Phase 7: Dark Mode (2 min)
- [ ] Scroll to bottom of page
- [ ] Look for dark mode toggle (if implemented)
- [ ] Toggle dark/light mode
- [ ] Verify colors adjust properly

---

## 🐛 TROUBLESHOOTING

### If Analytics Link Not Showing
```bash
# Check navigation is updated
grep -n "Analytics" templates/base.html
```

### If Dashboard 404
```bash
# Check URL config
python manage.py show_urls | grep analytics
```

### If API Returns Error
1. Open DevTools (F12)
2. Go to Console tab
3. Check for JavaScript errors
4. Check Network tab for API response
5. Verify user is logged in
6. Check server logs for Python errors

### If Server Crashed
```bash
# Restart server
pkill -9 -f runserver
python manage.py runserver 0.0.0.0:8000
```

### Common Errors

**ImportError: cannot import name 'UserBookInteraction'**
- ✅ FIXED: Changed to use ReaderActivity, BookRating, ReadingSession
- Run: `python manage.py migrate`

**TemplateDoesNotExist: analytics/dashboard.html**
- Check: `ls -la templates/analytics/`
- Verify: File exists and is spelled correctly

**No data in charts**
- This is NORMAL for new users/accounts
- Charts will show data once users have activity
- API endpoints will return empty arrays/zeros

---

## 📊 EXPECTED BEHAVIOR

### When First Created Account
- Stat cards show: 0 books, 0 pages, 0 rating
- Charts are empty (no data)
- Library stats show: 0 library books, 0 favorites, etc.
- This is CORRECT - no activity yet

### After Adding Test Data
- Create reading sessions
- Add book ratings
- Mark books as favorites
- Library stats will update automatically

### API Responses Format
```json
{
  "success": true,
  "data": {
    "books_read": 5,
    "total_pages": 1234,
    "avg_rating": 4.2,
    "ratings_given": 3,
    "total_interactions": 15
  }
}
```

---

## 🎯 SUCCESS CRITERIA

✅ Dashboard loads without errors  
✅ All charts render  
✅ Date filtering works  
✅ 7 API endpoints respond with JSON  
✅ Data updates when filter changes  
✅ Responsive on mobile/tablet/desktop  
✅ No JavaScript errors in console  
✅ Navigation link appears and works  

---

## 📝 NOTES

- Server: http://localhost:8000/fr/
- Analytics: http://localhost:8000/fr/analytics/
- Django Version: 6.0
- Database: SQLite (db.sqlite3)
- User Model: CustomUser (users/models.py)

---

## 🔗 QUICK LINKS

- [Dashboard](http://localhost:8000/fr/analytics/)
- [API Stats](http://localhost:8000/fr/analytics/api/stats/?days=30)
- [API Trends](http://localhost:8000/fr/analytics/api/trends/?days=30)
- [API Genres](http://localhost:8000/fr/analytics/api/genres/?limit=5)
- [API Library](http://localhost:8000/fr/analytics/api/library/)
- [API Recommendations](http://localhost:8000/fr/analytics/api/recommendations/?days=30)
- [API Reading Pace](http://localhost:8000/fr/analytics/api/reading-pace/?days=30)
- [API Monthly](http://localhost:8000/fr/analytics/api/monthly-comparison/)

---

## ✨ NEXT STEPS AFTER TESTING

1. **If Everything Works:**
   - Great! System is ready
   - You can now add test data
   - Run full test suite: `python manage.py test tests.test_analytics_dashboard`
   - Prepare for deployment

2. **If Issues Found:**
   - Check troubleshooting section
   - Review server logs
   - Check Django system checks: `python manage.py check`
   - Run: `python manage.py migrate` (if needed)

3. **To Stop Server:**
   ```bash
   pkill -9 -f runserver
   # or press CTRL+C in terminal
   ```

---

**Good luck with testing! 🚀**
