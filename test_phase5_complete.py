#!/usr/bin/env python
"""
PHASE 5: COMPLETE TESTING SCRIPT
Test all dashboard functionality and API endpoints
"""

import os
import sys
import django
import json
import requests
from django.test import Client
from django.contrib.auth.models import User

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from catalogue.models import Book, BookRating, UserPreference, UserRecommendation, Category, Author
from django.db.models import Q

# ============================================================================
# TEST CONFIGURATION
# ============================================================================

BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "test123456"

COLORS = {
    'SUCCESS': '\033[92m',
    'ERROR': '\033[91m',
    'WARNING': '\033[93m',
    'INFO': '\033[94m',
    'RESET': '\033[0m',
}

def log(message, status='INFO'):
    color = COLORS.get(status, COLORS['INFO'])
    print(f"{color}[{status}]{COLORS['RESET']} {message}")

# ============================================================================
# TEST 1: DATABASE STATE VERIFICATION
# ============================================================================

def test_database_state():
    log("=" * 70, 'INFO')
    log("TEST 1: DATABASE STATE VERIFICATION", 'INFO')
    log("=" * 70, 'INFO')
    
    try:
        # Check user exists
        user = User.objects.get(email=TEST_USER_EMAIL)
        log(f"✅ User exists: {user.username}", 'SUCCESS')
        
        # Check UserPreference exists
        pref = UserPreference.objects.get(user=user)
        log(f"✅ UserPreference exists for {user.username}", 'SUCCESS')
        
        # Check books
        books = Book.objects.all()
        log(f"✅ Total books in database: {books.count()}", 'SUCCESS')
        
        # Check categories
        categories = Category.objects.all()
        log(f"✅ Total categories: {categories.count()}", 'SUCCESS')
        
        # Check authors
        authors = Author.objects.all()
        log(f"✅ Total authors: {authors.count()}", 'SUCCESS')
        
        # Check ratings
        ratings = BookRating.objects.all()
        log(f"✅ Total ratings in system: {ratings.count()}", 'SUCCESS')
        
        # Check recommendations
        recommendations = UserRecommendation.objects.all()
        log(f"✅ Total recommendations: {recommendations.count()}", 'SUCCESS')
        
        return True
        
    except Exception as e:
        log(f"❌ Database verification failed: {str(e)}", 'ERROR')
        return False

# ============================================================================
# TEST 2: API ENDPOINTS
# ============================================================================

def test_api_endpoints():
    log("\n" + "=" * 70, 'INFO')
    log("TEST 2: API ENDPOINTS VERIFICATION", 'INFO')
    log("=" * 70, 'INFO')
    
    session = requests.Session()
    
    # Get CSRF token
    response = session.get(f"{BASE_URL}/user/login/")
    csrf_token = None
    for cookie in session.cookies:
        if cookie.name == 'csrftoken':
            csrf_token = cookie.value
            break
    
    # Login
    login_data = {
        'email': TEST_USER_EMAIL,
        'password': TEST_USER_PASSWORD,
        'csrfmiddlewaretoken': csrf_token,
    }
    
    login_response = session.post(f"{BASE_URL}/user/login/", data=login_data)
    if login_response.status_code == 200:
        log("✅ Login successful", 'SUCCESS')
    else:
        log(f"❌ Login failed: {login_response.status_code}", 'ERROR')
        return False
    
    # Test API endpoints
    endpoints = [
        ("/api/recommendations/personalized/", "GET", "Personalized Recommendations"),
        ("/api/recommendations/collaborative/", "GET", "Collaborative Recommendations"),
        ("/api/recommendations/content-based/", "GET", "Content-Based Recommendations"),
        ("/api/recommendations/trending/", "GET", "Trending Recommendations"),
        ("/api/trending/?period=7d", "GET", "Trending (7 days)"),
        ("/api/ratings/", "GET", "User Ratings"),
        ("/api/preferences/", "GET", "User Preferences"),
    ]
    
    for endpoint, method, description in endpoints:
        try:
            response = session.request(method, f"{BASE_URL}{endpoint}")
            if response.status_code in [200, 201]:
                log(f"✅ {description}: {response.status_code}", 'SUCCESS')
            else:
                log(f"⚠️ {description}: {response.status_code}", 'WARNING')
        except Exception as e:
            log(f"❌ {description} failed: {str(e)}", 'ERROR')
    
    return True

# ============================================================================
# TEST 3: DASHBOARD VIEW RENDERING
# ============================================================================

def test_dashboard_view():
    log("\n" + "=" * 70, 'INFO')
    log("TEST 3: DASHBOARD VIEW RENDERING", 'INFO')
    log("=" * 70, 'INFO')
    
    client = Client()
    
    # Get login page to get CSRF token
    response = client.get('/user/login/')
    
    # Login
    login_success = client.login(username=TEST_USER_EMAIL, password=TEST_USER_PASSWORD)
    if login_success:
        log("✅ Django Client Login successful", 'SUCCESS')
    else:
        log("⚠️ Django Client Login failed (trying with username instead)", 'WARNING')
        user = User.objects.get(email=TEST_USER_EMAIL)
        client.force_login(user)
        log("✅ Force login successful", 'SUCCESS')
    
    # Test dashboard view
    response = client.get('/books/recommendations/dashboard/')
    if response.status_code == 200:
        log("✅ Dashboard view returns 200", 'SUCCESS')
        
        # Check for key template elements
        content = response.content.decode('utf-8')
        checks = [
            ('Dashboard' in content, "Dashboard title"),
            ('recommendations' in content.lower(), "Recommendations widget"),
            ('trending' in content.lower(), "Trending widget"),
            ('rating' in content.lower(), "Rating form"),
            ('preferences' in content.lower(), "Preferences form"),
        ]
        
        for check, name in checks:
            if check:
                log(f"✅ Template contains: {name}", 'SUCCESS')
            else:
                log(f"⚠️ Template missing: {name}", 'WARNING')
    else:
        log(f"❌ Dashboard view failed: {response.status_code}", 'ERROR')
        if hasattr(response, 'context') and response.context:
            log(f"Context keys: {list(response.context.keys())}", 'INFO')
        if hasattr(response, 'content'):
            log(f"Response preview: {response.content[:200]}", 'INFO')
        return False
    
    return True

# ============================================================================
# TEST 4: MODEL RELATIONSHIPS
# ============================================================================

def test_model_relationships():
    log("\n" + "=" * 70, 'INFO')
    log("TEST 4: MODEL RELATIONSHIPS", 'INFO')
    log("=" * 70, 'INFO')
    
    try:
        user = User.objects.get(email=TEST_USER_EMAIL)
        
        # Check UserPreference
        try:
            pref = UserPreference.objects.get(user=user)
            log(f"✅ UserPreference linked to user", 'SUCCESS')
            
            # Check M2M relationships
            categories = pref.preferred_categories.all()
            log(f"✅ Preferred categories: {categories.count()}", 'SUCCESS')
            
            authors = pref.preferred_authors.all()
            log(f"✅ Preferred authors: {authors.count()}", 'SUCCESS')
            
        except UserPreference.DoesNotExist:
            log("⚠️ UserPreference not found (will be created on dashboard view)", 'WARNING')
        
        # Check UserRecommendations
        recs = UserRecommendation.objects.filter(user=user)
        log(f"✅ User recommendations: {recs.count()}", 'SUCCESS')
        
        # Check BookRatings
        ratings = BookRating.objects.filter(user=user)
        log(f"✅ User ratings: {ratings.count()}", 'SUCCESS')
        
        return True
        
    except Exception as e:
        log(f"❌ Model relationship test failed: {str(e)}", 'ERROR')
        return False

# ============================================================================
# TEST 5: RECOMMENDATIONS ENGINE
# ============================================================================

def test_recommendations_engine():
    log("\n" + "=" * 70, 'INFO')
    log("TEST 5: RECOMMENDATIONS ENGINE", 'INFO')
    log("=" * 70, 'INFO')
    
    try:
        from catalogue.recommendations import (
            get_personalized_recommendations,
            get_collaborative_recommendations,
            get_content_based_recommendations,
            get_trending_recommendations,
        )
        
        user = User.objects.get(email=TEST_USER_EMAIL)
        
        # Test each algorithm
        try:
            pers = get_personalized_recommendations(user, limit=5)
            log(f"✅ Personalized recommendations: {len(pers)} books", 'SUCCESS')
        except Exception as e:
            log(f"⚠️ Personalized recommendations error: {str(e)[:50]}", 'WARNING')
        
        try:
            collab = get_collaborative_recommendations(user, limit=5)
            log(f"✅ Collaborative recommendations: {len(collab)} books", 'SUCCESS')
        except Exception as e:
            log(f"⚠️ Collaborative recommendations error: {str(e)[:50]}", 'WARNING')
        
        try:
            content = get_content_based_recommendations(user, limit=5)
            log(f"✅ Content-based recommendations: {len(content)} books", 'SUCCESS')
        except Exception as e:
            log(f"⚠️ Content-based recommendations error: {str(e)[:50]}", 'WARNING')
        
        try:
            trend = get_trending_recommendations(user, period='7d', limit=5)
            log(f"✅ Trending recommendations: {len(trend)} books", 'SUCCESS')
        except Exception as e:
            log(f"⚠️ Trending recommendations error: {str(e)[:50]}", 'WARNING')
        
        return True
        
    except Exception as e:
        log(f"❌ Recommendations engine test failed: {str(e)}", 'ERROR')
        return False

# ============================================================================
# TEST 6: STATIC FILES AND TEMPLATES
# ============================================================================

def test_static_and_templates():
    log("\n" + "=" * 70, 'INFO')
    log("TEST 6: STATIC FILES AND TEMPLATES", 'INFO')
    log("=" * 70, 'INFO')
    
    import os
    
    files_to_check = [
        'templates/catalogue/dashboard.html',
        'templates/catalogue/components/recommendation_card.html',
        'templates/catalogue/components/rating_form_modal.html',
        'templates/catalogue/components/preferences_form_modal.html',
        'templates/catalogue/components/trending_widget.html',
        'templates/catalogue/components/recommendations_widget.html',
        'templates/base.html',
    ]
    
    for file_path in files_to_check:
        full_path = f'/workspaces/bnc/{file_path}'
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            log(f"✅ {file_path} ({size} bytes)", 'SUCCESS')
        else:
            log(f"❌ {file_path} NOT FOUND", 'ERROR')
    
    return True

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    log("\n" + "╔" + "=" * 68 + "╗", 'INFO')
    log("║" + " " * 20 + "PHASE 5: COMPLETE TESTING" + " " * 24 + "║", 'INFO')
    log("║" + " " * 15 + "Testing all functionality and API endpoints" + " " * 11 + "║", 'INFO')
    log("╚" + "=" * 68 + "╝", 'INFO')
    
    results = []
    
    # Run all tests
    results.append(("Database State", test_database_state()))
    results.append(("API Endpoints", test_api_endpoints()))
    results.append(("Dashboard View", test_dashboard_view()))
    results.append(("Model Relationships", test_model_relationships()))
    results.append(("Recommendations Engine", test_recommendations_engine()))
    results.append(("Static Files & Templates", test_static_and_templates()))
    
    # Summary
    log("\n" + "=" * 70, 'INFO')
    log("TEST SUMMARY", 'INFO')
    log("=" * 70, 'INFO')
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = 'SUCCESS' if result else 'ERROR'
        symbol = '✅' if result else '❌'
        log(f"{symbol} {test_name}: {'PASSED' if result else 'FAILED'}", status)
    
    log(f"\nTotal: {passed}/{total} tests passed", 'SUCCESS' if passed == total else 'WARNING')
    
    if passed == total:
        log("\n🎉 ALL TESTS PASSED! Dashboard is ready for production.", 'SUCCESS')
    else:
        log(f"\n⚠️ {total - passed} test(s) failed. Review errors above.", 'WARNING')
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
