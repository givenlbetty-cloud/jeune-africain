from unittest.mock import patch

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.db import IntegrityError, transaction
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.test import RequestFactory, TestCase, override_settings

from catalogue.admin import AuthorBookConflict, AuthorBookInlineFormSet, BookAdmin
from catalogue.models import Author, AuthorBook, Book


class AuthorBookConflictTests(TestCase):
    def setUp(self):
        self.book = Book.objects.create(title='Titre original')
        self.author = Author.objects.create(first_name='Alice', last_name='Dupont')
        self.formset_class = inlineformset_factory(
            Book, AuthorBook, formset=AuthorBookInlineFormSet,
            fields=('author', 'role', 'order'), extra=0,
        )

    def formset(self, link=None, **kwargs):
        data = {
            'authorbook_set-TOTAL_FORMS': '1',
            'authorbook_set-INITIAL_FORMS': '1' if link else '0',
            'authorbook_set-0-author': str(self.author.pk),
            'authorbook_set-0-role': 'primary',
            'authorbook_set-0-order': '0',
        }
        if link:
            data['authorbook_set-0-id'] = str(link.pk)
        return self.formset_class(data=data, instance=self.book, **kwargs)

    def test_insert_conflict_after_validation_is_reported(self):
        formset = self.formset()
        self.assertTrue(formset.is_valid(), formset.errors)
        existing = AuthorBook.objects.create(book=self.book, author=self.author, order=7)
        with self.assertRaises(AuthorBookConflict):
            formset.save()
        self.assertEqual(self.book.authorbook_set.get().pk, existing.pk)
        existing.refresh_from_db()
        self.assertEqual(existing.order, 7)

    def test_role_update_conflict_after_validation_is_reported(self):
        link = AuthorBook.objects.create(book=self.book, author=self.author, role='editor')
        formset = self.formset(link)
        self.assertTrue(formset.is_valid(), formset.errors)
        AuthorBook.objects.create(book=self.book, author=self.author, role='primary')
        with self.assertRaises(AuthorBookConflict):
            formset.save()
        link.refresh_from_db()
        self.assertEqual(link.role, 'editor')
        self.assertEqual(self.book.authorbook_set.count(), 2)

    def test_conflict_is_reported_even_if_competing_link_has_disappeared(self):
        formset = self.formset()
        self.assertTrue(formset.is_valid(), formset.errors)
        existing = AuthorBook.objects.create(book=self.book, author=self.author)
        # Capture a real backend exception, then simulate the competing row
        # disappearing before the inline handles that exception.
        with self.assertRaises(IntegrityError) as failure, transaction.atomic():
            AuthorBook.objects.create(book=self.book, author=self.author)
        existing.delete()
        with patch.object(BaseInlineFormSet, 'save_new', side_effect=failure.exception):
            with self.assertRaises(AuthorBookConflict):
                formset.save()
        self.assertFalse(self.book.authorbook_set.exists())

    def test_unrelated_integrity_error_is_not_hidden(self):
        formset = self.formset()
        self.assertTrue(formset.is_valid(), formset.errors)
        # Simulate a different database failure after validation.
        formset.forms[0].instance.order = -1
        with self.assertRaises(IntegrityError):
            formset.save()
        self.assertFalse(self.book.authorbook_set.exists())

    def test_database_still_rejects_duplicates(self):
        AuthorBook.objects.create(book=self.book, author=self.author)
        with self.assertRaises(IntegrityError), transaction.atomic():
            AuthorBook.objects.create(book=self.book, author=self.author)
        self.assertEqual(self.book.authorbook_set.count(), 1)

    def test_other_constraint_error_is_not_hidden_even_if_duplicate_exists(self):
        formset = self.formset()
        self.assertTrue(formset.is_valid(), formset.errors)
        AuthorBook.objects.create(book=self.book, author=self.author)
        formset.forms[0].instance.order = -1
        with self.assertRaises(IntegrityError):
            formset.save()
        self.assertEqual(self.book.authorbook_set.count(), 1)

    def test_conflict_flag_prevents_even_an_empty_submission_from_saving(self):
        formset = self.formset_class(
            data={'authorbook_set-TOTAL_FORMS': '0', 'authorbook_set-INITIAL_FORMS': '0'},
            instance=self.book, author_link_conflict=True,
        )
        self.assertFalse(formset.is_valid())
        self.assertIn('Aucune modification', str(formset.non_form_errors()))


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class BookAdminConflictResponseTests(TestCase):
    def setUp(self):
        self.admin = BookAdmin(Book, AdminSite())
        self.user = get_user_model().objects.create_superuser(
            username='author-admin', email='admin@example.com', password='test-password',
        )
        self.author = Author.objects.create(first_name='Alice', last_name='Dupont')
        self.book = Book.objects.create(title='Titre original')

    def request(self):
        data = {
            'title': 'Titre modifié', 'isbn': self.book.isbn,
            'language': 'fr', 'genre': 'other', 'price': '0',
            'discount_percentage': '0', 'free_pages_count': '15',
            'is_published': 'on',
            'authorbook_set-TOTAL_FORMS': '1', 'authorbook_set-INITIAL_FORMS': '0',
            'authorbook_set-0-author': str(self.author.pk),
            'authorbook_set-0-role': 'primary', 'authorbook_set-0-order': '2',
        }
        factory = RequestFactory()
        permissions_request = factory.get('/')
        permissions_request.user = self.user
        for formset_class, _ in self.admin.get_formsets_with_inlines(permissions_request, self.book):
            prefix = formset_class.get_default_prefix()
            if prefix != 'authorbook_set':
                data[f'{prefix}-TOTAL_FORMS'] = '0'
                data[f'{prefix}-INITIAL_FORMS'] = '0'
        request = factory.post(f'/fr/admin/catalogue/book/{self.book.pk}/change/', data)
        request.user = self.user
        request.session = {}
        request._messages = FallbackStorage(request)
        request._dont_enforce_csrf_checks = True
        return request

    def test_conflict_rolls_back_book_and_redisplays_bound_form(self):
        request = self.request()
        save_related = self.admin.save_related

        def competing_insert(request, form, formsets, change):
            # Inject the competing row at the actual check/write boundary.
            AuthorBook.objects.create(book=form.instance, author=self.author)
            save_related(request, form, formsets, change)

        with patch.object(self.admin, 'save_related', side_effect=competing_insert) as save:
            response = self.admin.changeform_view(request, str(self.book.pk))
        self.assertEqual(save.call_count, 1)  # The error response must not retry saving.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['adminform'].form['title'].value(), 'Titre modifié')
        author_forms = response.context_data['inline_admin_formsets'][0].formset
        self.assertIn('Aucune modification', str(author_forms.non_form_errors()))
        self.assertEqual(author_forms.forms[0]['author'].value(), str(self.author.pk))
        self.assertFalse(hasattr(request, '_author_link_conflict'))
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, 'Titre original')
        self.assertFalse(self.book.authorbook_set.exists())

    def test_unrelated_database_failure_is_not_retried_or_masked(self):
        request = self.request()
        with patch.object(self.admin, 'save_related', side_effect=IntegrityError('unrelated')) as save:
            with self.assertRaises(IntegrityError):
                self.admin.changeform_view(request, str(self.book.pk))
        self.assertEqual(save.call_count, 1)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, 'Titre original')
