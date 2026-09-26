from unittest.mock import Mock

from django.contrib.admin.sites import AdminSite
from django.forms.models import inlineformset_factory
from django.test import TestCase

from catalogue.admin import AuthorBookInlineFormSet, BookAdmin
from catalogue.models import Author, AuthorBook, Book


class BookAdminAuthorsTests(TestCase):
    def setUp(self):
        self.admin = BookAdmin(Book, AdminSite())
        self.author = Author.objects.create(first_name='Alice', last_name='Dupont')
        self.formset_class = inlineformset_factory(
            Book, AuthorBook, formset=AuthorBookInlineFormSet,
            fields=('author', 'role', 'order'), extra=0,
        )

    def save_book_with_authors(self, authors, change=False):
        book = Book(title='Un livre - Alice Dupont', pages_count=10,
                    cover='covers/existing.jpg')
        if change:
            book.save()
        book.pdf_file = 'books/example.pdf'
        data = {'authorbook_set-TOTAL_FORMS': str(len(authors)),
                'authorbook_set-INITIAL_FORMS': '0'}
        for index, author in enumerate(authors):
            data.update({f'authorbook_set-{index}-author': str(author.pk),
                         f'authorbook_set-{index}-role': 'primary',
                         f'authorbook_set-{index}-order': '2'})
        formset = self.formset_class(data=data, instance=book)
        self.assertTrue(formset.is_valid(), formset.errors)
        form = Mock(instance=book)
        self.admin.save_model(None, book, form, change)
        self.admin.save_related(None, form, [formset], change)
        return book

    def test_explicit_inferred_author_is_saved_once_on_add_and_change(self):
        for change in (False, True):
            with self.subTest(change=change):
                book = self.save_book_with_authors([self.author], change)
                link = book.authorbook_set.get()
                self.assertEqual(link.author, self.author)
                self.assertEqual(link.order, 2)

    def test_explicit_author_takes_precedence_over_inferred_author(self):
        other = Author.objects.create(first_name='Jean', last_name='Martin')
        book = self.save_book_with_authors([other])
        self.assertEqual(book.authorbook_set.get().author, other)

    def test_empty_inline_still_infers_author(self):
        book = self.save_book_with_authors([])
        self.assertEqual(book.authorbook_set.get().author, self.author)

    def test_normal_model_save_still_infers_author(self):
        book = Book.objects.create(title='Un livre - Alice Dupont', pages_count=10,
                                   pdf_file='books/example.pdf', cover='covers/existing.jpg')
        self.assertEqual(book.authorbook_set.get().author, self.author)

    def test_duplicate_inline_authors_are_invalid(self):
        book = Book(title='Un livre')
        data = {'authorbook_set-TOTAL_FORMS': '2', 'authorbook_set-INITIAL_FORMS': '0'}
        for index in range(2):
            data.update({f'authorbook_set-{index}-author': str(self.author.pk),
                         f'authorbook_set-{index}-role': 'primary',
                         f'authorbook_set-{index}-order': '0'})
        self.assertFalse(self.formset_class(data=data, instance=book).is_valid())
