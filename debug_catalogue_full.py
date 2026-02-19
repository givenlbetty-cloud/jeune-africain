import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from catalogue.models import Book

print(f"Total books: {Book.objects.count()}")
print(f"Published books: {Book.objects.filter(is_published=True).count()}")
print(f"Books without authors: {Book.objects.filter(authors__isnull=True).count()}")
books_no_auth = Book.objects.filter(authors__isnull=True)
print(f"Published Books without authors: {books_no_auth.filter(is_published=True).count()}")

# Simulate view query
books = Book.objects.filter(is_published=True).order_by('-created_at')
print(f"View Query count: {books.count()}")
for b in books:
    print(f" - {b.title} (Published: {b.is_published}) [Author: {b.author}]")
