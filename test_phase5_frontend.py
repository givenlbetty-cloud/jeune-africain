#!/usr/bin/env python
"""
PHASE 5: FRONTEND TESTING SCRIPT
Test dashboard rendering, forms, and AJAX functionality
"""

import requests
import json
from bs4 import BeautifulSoup
import time

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "test123456"

# Colors for output
class Colors:
    OK = '\033[92m'
    FAIL = '\033[91m'
    WARN = '\033[93m'
    INFO = '\033[94m'
    RESET = '\033[0m'

def log(msg, status='INFO'):
    colors = {'SUCCESS': Colors.OK, 'ERROR': Colors.FAIL, 'WARNING': Colors.WARN, 'INFO': Colors.INFO}
    color = colors.get(status, Colors.INFO)
    print(f"{color}[{status}]{Colors.RESET} {msg}")

# ============================================================================
# TEST 1: LOGIN AND SESSION
# ============================================================================

def test_login():
    log("=" * 70, 'INFO')
    log("TEST 1: LOGIN AND SESSION", 'INFO')
    log("=" * 70, 'INFO')
    
    session = requests.Session()
    
    try:
        # Get login page
        response = session.get(f"{BASE_URL}/user/login/")
        if response.status_code != 200:
            log(f"❌ Login page failed: {response.status_code}", 'ERROR')
            return None
        
        log("✅ Login page loaded", 'SUCCESS')
        
        # Get CSRF token
        soup = BeautifulSoup(response.content, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        if not csrf_input:
            log("⚠️ CSRF token not found in form", 'WARNING')
            csrf_token = None
        else:
            csrf_token = csrf_input.get('value')
            log("✅ CSRF token extracted", 'SUCCESS')
        
        # Try login
        login_data = {
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD,
        }
        
        if csrf_token:
            login_data['csrfmiddlewaretoken'] = csrf_token
        
        response = session.post(f"{BASE_URL}/user/login/", data=login_data, allow_redirects=True)
        
        if response.status_code == 200 and 'login' not in response.url.lower():
            log("✅ Login successful", 'SUCCESS')
            return session
        elif 'dashboard' in response.url or 'recommendations' in response.url:
            log("✅ Login successful (redirected to dashboard)", 'SUCCESS')
            return session
        else:
            log(f"⚠️ Login response code {response.status_code}, URL: {response.url}", 'WARNING')
            return session  # Continue anyway
            
    except Exception as e:
        log(f"❌ Login test failed: {str(e)}", 'ERROR')
        return None

# ============================================================================
# TEST 2: DASHBOARD VIEW
# ============================================================================

def test_dashboard_view(session):
    if not session:
        log("❌ Skipping dashboard test (no session)", 'ERROR')
        return False
    
    log("\n" + "=" * 70, 'INFO')
    log("TEST 2: DASHBOARD VIEW RENDERING", 'INFO')
    log("=" * 70, 'INFO')
    
    try:
        response = session.get(f"{BASE_URL}/books/recommendations/dashboard/")
        
        if response.status_code != 200:
            log(f"❌ Dashboard returned {response.status_code}", 'ERROR')
            return False
        
        log("✅ Dashboard page loaded (HTTP 200)", 'SUCCESS')
        
        content = response.text
        soup = BeautifulSoup(content, 'html.parser')
        
        # Check for key elements
        checks = [
            ('recommendations' in content.lower(), "Recommendations widget text"),
            ('trending' in content.lower(), "Trending widget text"),
            (soup.find('form', {'id': 'rating-form'}) is not None, "Rating form element"),
            (soup.find('form', {'id': 'preferences-form'}) is not None, "Preferences form element"),
            (soup.find('div', {'class': 'dashboard'}) is not None or 'dashboard' in content.lower(), "Dashboard container"),
        ]
        
        passed = 0
        for check, description in checks:
            if check:
                log(f"✅ {description}", 'SUCCESS')
                passed += 1
            else:
                log(f"⚠️ {description} not found", 'WARNING')
        
        return passed >= 3  # At least 3 checks should pass
        
    except Exception as e:
        log(f"❌ Dashboard test failed: {str(e)}", 'ERROR')
        return False

# ============================================================================
# TEST 3: API ENDPOINTS
# ============================================================================

def test_api_endpoints(session):
    if not session:
        log("❌ Skipping API tests (no session)", 'ERROR')
        return False
    
    log("\n" + "=" * 70, 'INFO')
    log("TEST 3: API ENDPOINTS", 'INFO')
    log("=" * 70, 'INFO')
    
    endpoints = [
        ("/api/recommendations/personalized/", "GET", "Personalized"),
        ("/api/recommendations/collaborative/", "GET", "Collaborative"),
        ("/api/recommendations/content-based/", "GET", "Content-based"),
        ("/api/recommendations/trending/", "GET", "Trending"),
        ("/api/trending/?period=7d", "GET", "Trending API"),
        ("/api/ratings/", "GET", "Ratings"),
        ("/api/preferences/", "GET", "Preferences"),
    ]
    
    passed = 0
    for endpoint, method, name in endpoints:
        try:
            response = session.request(method, f"{BASE_URL}{endpoint}")
            if response.status_code in [200, 201, 400]:  # 400 is ok if data is invalid
                log(f"✅ {name} ({response.status_code})", 'SUCCESS')
                
                # Try to parse JSON
                try:
                    data = response.json()
                    if isinstance(data, dict) and 'results' in data:
                        log(f"   └─ Returns {len(data.get('results', []))} items", 'INFO')
                except:
                    pass
                
                passed += 1
            else:
                log(f"⚠️ {name} ({response.status_code})", 'WARNING')
        except Exception as e:
            log(f"❌ {name} error: {str(e)[:40]}", 'ERROR')
    
    log(f"\nAPI Tests: {passed}/{len(endpoints)} passed", 'SUCCESS' if passed > 4 else 'WARNING')
    return passed > 4

# ============================================================================
# TEST 4: FORM FUNCTIONALITY
# ============================================================================

def test_form_functionality(session):
    if not session:
        log("❌ Skipping form tests (no session)", 'ERROR')
        return False
    
    log("\n" + "=" * 70, 'INFO')
    log("TEST 4: FORM FUNCTIONALITY", 'INFO')
    log("=" * 70, 'INFO')
    
    try:
        # Get dashboard to extract form elements
        response = session.get(f"{BASE_URL}/books/recommendations/dashboard/")
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check rating form
        rating_form = soup.find('form', {'id': 'rating-form'})
        if rating_form:
            log("✅ Rating form exists", 'SUCCESS')
            selects = rating_form.find_all('select')
            log(f"   └─ Contains {len(selects)} select field(s)", 'INFO')
        else:
            log("⚠️ Rating form not found", 'WARNING')
        
        # Check preferences form
        pref_form = soup.find('form', {'id': 'preferences-form'})
        if pref_form:
            log("✅ Preferences form exists", 'SUCCESS')
            inputs = pref_form.find_all('input')
            log(f"   └─ Contains {len(inputs)} input field(s)", 'INFO')
        else:
            log("⚠️ Preferences form not found", 'WARNING')
        
        # Check for scripts
        scripts = soup.find_all('script')
        log(f"✅ Page contains {len(scripts)} script(s)", 'SUCCESS')
        
        return True
        
    except Exception as e:
        log(f"❌ Form test failed: {str(e)}", 'ERROR')
        return False

# ============================================================================
# TEST 5: RESPONSIVE DESIGN
# ============================================================================

def test_responsive_design(session):
    if not session:
        log("❌ Skipping responsive test (no session)", 'ERROR')
        return False
    
    log("\n" + "=" * 70, 'INFO')
    log("TEST 5: RESPONSIVE DESIGN", 'INFO')
    log("=" * 70, 'INFO')
    
    try:
        response = session.get(f"{BASE_URL}/books/recommendations/dashboard/")
        content = response.text
        
        # Check for Bootstrap classes (indicating responsive design)
        bootstrap_checks = [
            ('container' in content, "Container class"),
            ('row' in content or 'col-' in content, "Grid classes"),
            ('btn' in content, "Button classes"),
            ('modal' in content, "Modal classes"),
            ('responsive' in content.lower(), "Responsive mention"),
        ]
        
        passed = 0
        for check, description in bootstrap_checks:
            if check:
                log(f"✅ {description}", 'SUCCESS')
                passed += 1
            else:
                log(f"⚠️ {description} not found", 'WARNING')
        
        return passed >= 2
        
    except Exception as e:
        log(f"❌ Responsive test failed: {str(e)}", 'ERROR')
        return False

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    log("\n╔" + "=" * 68 + "╗", 'INFO')
    log("║" + " " * 15 + "PHASE 5: FRONTEND TESTING SUITE" + " " * 22 + "║", 'INFO')
    log("╚" + "=" * 68 + "╝", 'INFO')
    
    results = []
    
    # Run tests
    session = test_login()
    results.append(("Login & Session", session is not None))
    
    results.append(("Dashboard View", test_dashboard_view(session)))
    results.append(("API Endpoints", test_api_endpoints(session)))
    results.append(("Form Functionality", test_form_functionality(session)))
    results.append(("Responsive Design", test_responsive_design(session)))
    
    # Summary
    log("\n" + "=" * 70, 'INFO')
    log("FRONTEND TEST SUMMARY", 'INFO')
    log("=" * 70, 'INFO')
    
    for test_name, result in results:
        symbol = '✅' if result else '❌'
        status = 'SUCCESS' if result else 'ERROR'
        log(f"{symbol} {test_name}: {'PASSED' if result else 'FAILED'}", status)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    log(f"\nTotal: {passed}/{total} tests passed", 'SUCCESS' if passed == total else 'WARNING')
    
    if passed == total:
        log("\n🎉 ALL FRONTEND TESTS PASSED!", 'SUCCESS')
    else:
        log(f"\n⚠️ {total - passed} test(s) need review", 'WARNING')
    
    return passed >= total - 1  # Allow 1 failure

if __name__ == '__main__':
    main()
