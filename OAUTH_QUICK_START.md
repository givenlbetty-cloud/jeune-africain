# 🚀 Quick Start OAuth Testing - BNC

## ⏱️ Time to Functional OAuth: ~15 minutes

### Step 1: Get Google OAuth Credentials (5 minutes)

1. **Go to Google Cloud Console**
   ```
   https://console.cloud.google.com/
   ```

2. **Create a New Project**
   - Click "Select a Project" → "NEW PROJECT"
   - Name: `BNC Development`
   - Click "CREATE"

3. **Enable Google+ API**
   - Go to "APIs & Services" → "Library"
   - Search for "Google+ API"
   - Click and press "ENABLE"

4. **Create OAuth Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Name: `BNC Local`
   - Under "Authorized redirect URIs", add:
     ```
     http://localhost:8000/auth/google/callback/
     http://127.0.0.1:8000/auth/google/callback/
     ```
   - Click "CREATE"
   - **Copy the Client ID and Secret** from the popup

### Step 2: Setup OAuth (1 minute)

```bash
cd /workspaces/bnc

# Using the management command
python manage.py setup_oauth --provider google \
    --client-id "YOUR_CLIENT_ID.apps.googleusercontent.com" \
    --client-secret "YOUR_CLIENT_SECRET"

# Expected output:
# ✅ Created Google OAuth app
#    Name: Google
#    Provider: google
#    Assigned to site: example.com
```

### Step 3: Test OAuth (5 minutes)

1. **Start Django Server**
   ```bash
   python manage.py runserver
   ```
   You should see: `Starting development server at http://0.0.0.0:8000/`

2. **Open Login Page in Browser**
   ```
   http://localhost:8000/auth/login/
   ```
   
   You should see:
   - Email field
   - Password field
   - "Continue with Google" button
   - Registration link

3. **Test Google OAuth Flow**
   - Click "Continue with Google"
   - You're redirected to Google login
   - Sign in with your Google account
   - Grant permission to BNC
   - You're redirected back to BNC
   - **New account is created automatically** ✅
   - **You're logged in and redirected to books catalogue** ✅

4. **Verify Success**
   - You see the book catalogue (user menu at top-right)
   - Your name appears in the user menu
   - Click logout → redirects to home page

### Step 4: Verify Setup (5 minutes)

```bash
# Check configured OAuth apps
python manage.py setup_oauth --list

# Expected output:
# ✅ Configured OAuth Applications:
# ════════════════════════════════════════════════════════════════════════════════
# 
# 📱 Google
#    Provider: google
#    Client ID: 123456789-abc...
#    Sites: example.com

# Run full test suite
./test_oauth.sh
```

---

## ✅ Manual Testing Checklist

After setup, verify:

- [ ] Can click "Continue with Google" without errors
- [ ] Redirected to Google login
- [ ] Can authenticate with Google account
- [ ] Granted permission to BNC
- [ ] Redirected back to http://localhost:8000/auth/google/callback/
- [ ] New account created in BNC (check `/admin/users/customuser/`)
- [ ] Logged in (user menu visible at top-right)
- [ ] Redirected to books catalogue page
- [ ] Can click on book to view details
- [ ] Can logout and return to login page
- [ ] Can login again with same Google account (account linking works)

---

## 🐛 Troubleshooting

### Problem: "Redirect URI mismatch" Error

**Cause**: Redirect URI in Google Console doesn't match BNC

**Fix**:
1. Go to https://console.cloud.google.com/
2. Find your OAuth app credentials
3. Click edit
4. Update "Authorized redirect URIs":
   ```
   http://localhost:8000/auth/google/callback/
   ```
5. Save and try again

### Problem: "OAuth app not found" Error

**Cause**: OAuth app not created in Django

**Fix**:
```bash
python manage.py setup_oauth --list
# If empty, run:
python manage.py setup_oauth --provider google \
    --client-id YOUR_CLIENT_ID \
    --client-secret YOUR_CLIENT_SECRET
```

### Problem: Button doesn't appear on login page

**Cause**: OAuth app not assigned to site

**Fix**:
1. Check Django admin: http://localhost:8000/admin/
2. Go to "Social Applications"
3. Click "Google" app
4. Under "Sites", make sure "example.com" is selected
5. Save

### Problem: Server crashes when visiting login page

**Cause**: Template syntax error

**Fix**:
```bash
python manage.py check
# Should show: "System check identified 0 issues"
# (1 warning about ACCOUNT_LOGIN_METHODS is acceptable)
```

---

## 📱 Test Registration with OAuth

1. Visit: http://localhost:8000/auth/signup/
2. Click "Sign up with Google"
3. Complete Google authentication
4. New account created
5. Auto-logged in and redirected to catalogue

---

## 🔗 Useful Links

- **Django Admin**: http://localhost:8000/admin/
- **Social Applications**: http://localhost:8000/admin/socialaccount/socialapp/
- **Users**: http://localhost:8000/admin/users/customuser/
- **Login**: http://localhost:8000/auth/login/
- **Register**: http://localhost:8000/auth/signup/
- **Logout**: http://localhost:8000/auth/logout/
- **Books**: http://localhost:8000/catalogue/

---

## 📚 Full Documentation

See [OAUTH_INTEGRATION_GUIDE.md](OAUTH_INTEGRATION_GUIDE.md) for complete details.

---

## 🎯 What's Next?

After verifying OAuth works:

1. **Test Edge Cases**
   - Login with email → then OAuth (account linking)
   - OAuth → then forgot password (email recovery)
   - Multiple Google accounts

2. **Setup Other Providers** (Optional)
   - Apple OAuth
   - Windows OAuth
   - GitHub OAuth

3. **Production Deployment**
   - Use real domain
   - Setup HTTPS
   - Use real Google OAuth app
   - Update redirect URIs

4. **Next Feature**: Recommendations Engine (→ 90% completion)

---

## ✨ Success!

Once OAuth is working:
- ✅ 85% of cahier des charges complete
- ✅ Modern authentication system ready
- ✅ Next: Recommendations Algorithm (90%)

**Estimated time**: 15 minutes setup + 5 minutes testing = **20 minutes total**

---

*Quick Start Guide - December 19, 2025*
*OAuth Integration Complete*
