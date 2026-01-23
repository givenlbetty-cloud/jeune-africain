# 🚀 BNC Library - Quick Reference Guide

**Last Updated**: Dec 21, 2025  
**Status**: Production Ready ✅  
**Version**: 1.0.0  

---

## 📋 Table des Matières

1. [Setup & Installation](#setup--installation)
2. [Running Tests](#running-tests)
3. [Development Commands](#development-commands)
4. [Deployment](#deployment)
5. [Troubleshooting](#troubleshooting)
6. [API Endpoints](#api-endpoints)

---

## 🔧 Setup & Installation

### Initial Setup
```bash
# Clone repository
git clone https://github.com/your-org/bnc-library.git
cd bnc

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your settings

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Create test data (optional)
python manage.py loaddata fixtures/sample_data.json
```

### Development Server
```bash
# Start development server
python manage.py runserver

# Start on specific port
python manage.py runserver 0.0.0.0:8001

# With debug toolbar
python manage.py runserver --with-debug
```

---

## 🧪 Running Tests

### Quick Test Run
```bash
# All tests
python manage.py test

# Specific app
python manage.py test catalogue

# Specific test class
python manage.py test catalogue.tests.PaymentTests

# Specific test
python manage.py test catalogue.tests.PaymentTests.test_payment_creation

# Verbose output
python manage.py test catalogue -v 2

# With timing
python manage.py test catalogue --timing

# Stop on first failure
python manage.py test catalogue --failfast

# Parallel execution
python manage.py test catalogue --parallel 4
```

### Coverage Testing
```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='catalogue' manage.py test catalogue.tests

# Generate report
coverage report

# Generate HTML report
coverage html

# View HTML report
open htmlcov/index.html
```

### Test Patterns
```bash
# Run all tests except slow ones
python manage.py test catalogue -k "not slow"

# Run by pattern
python manage.py test catalogue -k "test_payment*"

# Run with specific settings
python manage.py test --settings=config.settings_test

# Keep test database
python manage.py test catalogue --keepdb
```

---

## 👨‍💻 Development Commands

### Database Management
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migrations
python manage.py showmigrations

# Reverse specific migration
python manage.py migrate catalogue 0001

# Create empty migration
python manage.py makemigrations --empty catalogue --name fix_something

# Check migrations
python manage.py check --deploy
```

### Django Admin
```bash
# Create superuser
python manage.py createsuperuser

# Change user password
python manage.py changepassword username

# Create groups and permissions
python manage.py shell < scripts/setup_permissions.py

# Dump data
python manage.py dumpdata --natural-foreign --natural-primary > data.json

# Load data
python manage.py loaddata data.json
```

### Static Files
```bash
# Collect static files
python manage.py collectstatic --noinput

# Find static files
python manage.py findstatic css/style.css

# Clear collectstatic cache
python manage.py collectstatic --clear --noinput

# Check if app has static files
python manage.py check --deploy
```

### Utilities
```bash
# Django shell with project imports
python manage.py shell

# Python shell with environment
python manage.py shell -i ipython  # requires ipython

# Check for issues
python manage.py check

# System check with deployment settings
python manage.py check --deploy

# Generate SECRET_KEY
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# List all management commands
python manage.py help

# Run custom command
python manage.py import_books --source=./books.csv
```

---

## 🚀 Deployment

### Pre-Deployment
```bash
# Check for deployment issues
python manage.py check --deploy

# Generate new SECRET_KEY
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Collect static files for production
python manage.py collectstatic --noinput --clear

# Test database
python manage.py migrate --dry-run

# Run full test suite
python manage.py test
```

### Deployment with Docker
```bash
# Build image
docker build -t bnc-library:latest .

# Run container
docker run -p 8000:8000 \
  -e DEBUG=False \
  -e ALLOWED_HOSTS=yourdomain.com \
  -e DATABASE_URL=postgresql://... \
  bnc-library:latest

# Run with compose
docker-compose up -d

# See logs
docker-compose logs -f web

# Execute command in container
docker-compose exec web python manage.py migrate
```

### Production Server (Gunicorn + Nginx)
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# Run in background
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --daemon

# With multiple workers
gunicorn config.wsgi:application --workers 4 --threads 2 --worker-class gthread
```

---

## 🐛 Troubleshooting

### Common Issues

#### Issue: `ModuleNotFoundError`
```bash
# Solution: Install dependencies
pip install -r requirements.txt

# Or update pip, setuptools
pip install --upgrade pip setuptools wheel
```

#### Issue: `ProgrammingError: relation "..." does not exist`
```bash
# Solution: Apply migrations
python manage.py migrate

# If migrations are broken, create new one
python manage.py makemigrations --empty catalogue --name fix_migration
python manage.py migrate
```

#### Issue: `SECRET_KEY not configured`
```bash
# Solution: Create .env file
echo "SECRET_KEY=$(python manage.py shell -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" > .env
```

#### Issue: `ALLOWED_HOSTS error`
```bash
# Solution: Update ALLOWED_HOSTS in settings.py or .env
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
```

#### Issue: Static files not loading
```bash
# Solution: Collect static files
python manage.py collectstatic --noinput

# Or check settings.py
# STATIC_URL, STATIC_ROOT, STATICFILES_DIRS should be configured
```

#### Issue: Database connection error
```bash
# Solution: Check DATABASE_URL
python manage.py dbshell  # Test connection

# Or check .env file has DATABASE_URL set
# DATABASE_URL=sqlite:///db.sqlite3 (dev)
# DATABASE_URL=postgresql://user:pass@localhost/bnc (prod)
```

### Debug Commands
```bash
# Check installed packages
pip list

# Check Django version
python manage.py --version

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Test imports
python -c "import catalogue; print('OK')"

# List all settings
python manage.py shell -c "from django.conf import settings; print(settings.DEBUG)"

# Check database tables
python manage.py shell -c "from django.db import connection; print(connection.introspection.table_names())"
```

---

## 📡 API Endpoints

### Books
```
GET    /api/books/                          # List all books
GET    /api/books/{id}/                     # Get book details
POST   /api/books/                          # Create book (admin)
PUT    /api/books/{id}/                     # Update book (admin)
DELETE /api/books/{id}/                     # Delete book (admin)
GET    /api/books/search/?q=...             # Search books
GET    /api/books/{id}/recommendations/     # Get recommendations
```

### Events
```
GET    /api/events/                         # List events
GET    /api/events/{id}/                    # Get event details
POST   /api/events/                         # Create event (admin)
PUT    /api/events/{id}/                    # Update event (admin)
DELETE /api/events/{id}/                    # Delete event (admin)
GET    /api/events/upcoming/                # Get upcoming events
GET    /api/events/{id}/stats/              # Get event statistics
POST   /api/events/{id}/register/           # Register for event
POST   /api/events/{id}/unregister/         # Unregister from event
```

### Payments
```
POST   /api/payments/mobile-money/{book_id}/              # Initiate payment
GET    /api/payments/mobile-money/{payment_id}/status/   # Check status
POST   /api/payments/webhook/mpesa/                       # M-Pesa webhook
POST   /api/payments/webhook/airtel/                      # Airtel webhook
POST   /api/payments/webhook/orange/                      # Orange webhook
GET    /api/payments/history/                             # Payment history
```

### Preview
```
GET    /api/book/{id}/can-read/             # Can read full book?
GET    /api/book/{id}/preview-pages/        # Get free pages count
GET    /api/book/{id}/page/{num}/access/    # Check page access
```

### Reading
```
GET    /api/reading/sessions/               # Get reading sessions
POST   /api/reading/sessions/               # Create session
PUT    /api/reading/sessions/{id}/          # Update session
GET    /api/reading/sessions/{id}/          # Get session details
POST   /api/reading/{book_id}/progress/     # Update progress
```

### Recommendations
```
GET    /api/recommendations/                # Get recommendations
GET    /api/recommendations/{book_id}/      # Similar books
GET    /api/books/trending/                 # Trending books
GET    /api/books/bestsellers/              # Best-rated books
```

### Authentication
```
POST   /api/auth/login/                     # Login
POST   /api/auth/logout/                    # Logout
POST   /api/auth/register/                  # Register
POST   /api/auth/refresh/                   # Refresh token
POST   /api/auth/token/                     # Get token
```

### Example Requests
```bash
# List books
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/books/

# Get book details
curl http://localhost:8000/api/books/123e4567-e89b-12d3-a456-426614174000/

# Initiate payment
curl -X POST http://localhost:8000/api/payments/mobile-money/123e4567-e89b-12d3-a456-426614174000/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+256701234567", "provider": "AIRTEL"}'

# Register for event
curl -X POST http://localhost:8000/api/events/abc-123/register/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json"

# Get recommendations
curl "http://localhost:8000/api/recommendations/?book_id=123-abc"
```

---

## 📚 Additional Resources

### Documentation
- [README.md](./README.md) - Project overview
- [API_DOCS.md](./API_DOCS.md) - API documentation
- [TESTING_SUITE.md](./TESTING_SUITE.md) - Testing guide
- [TESTING_RESULTS.md](./TESTING_RESULTS.md) - Test results

### External Links
- [Django Docs](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Docker Docs](https://docs.docker.com/)

### Development Tools
- Visual Studio Code: `code .`
- Django Admin: `http://localhost:8000/admin/`
- Database Client: pgAdmin, DBeaver
- API Client: Postman, Insomnia, Thunder Client

---

## 💬 Support

### Getting Help
1. Check [documentation](./README.md)
2. Search [issues](https://github.com/your-org/bnc-library/issues)
3. Read [test examples](./catalogue/tests.py)
4. Ask in discussions or Slack

### Reporting Issues
```bash
# Create issue with details
# Include:
# - Error message (full traceback)
# - Steps to reproduce
# - Expected vs actual behavior
# - Django/Python/Database versions
# - Environment (dev/staging/prod)
```

---

**Last Updated**: Dec 21, 2025  
**Maintainer**: GitHub Copilot  
**License**: MIT
