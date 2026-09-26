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

    def author_formset(self, book, rows, initial_forms=0):
        data = {
            'authorbook_set-TOTAL_FORMS': str(len(rows)),
            'authorbook_set-INITIAL_FORMS': str(initial_forms),
        }
        for index, row in enumerate(rows):
            data.update({
                f'authorbook_set-{index}-{field}': str(value)
                for field, value in row.items()
            })
        return self.formset_class(data=data, instance=book)

    def save_author_formset(self, book, formset, change=True):
        self.assertTrue(formset.is_valid(), (formset.errors, formset.non_form_errors()))
        form = Mock(instance=book)
        self.admin.save_model(None, book, form, change)
        self.admin.save_related(None, form, [formset], change)

    def test_existing_link_is_preserved_when_another_author_is_added(self):
        book = self.save_book_with_authors([self.author])
        original = book.authorbook_set.get()
        other = Author.objects.create(first_name='Jean', last_name='Martin')
        formset = self.author_formset(book, [
            {'id': original.pk, 'author': self.author.pk, 'role': 'primary', 'order': 2},
            {'author': other.pk, 'role': 'primary', 'order': 3},
        ], initial_forms=1)

        self.save_author_formset(book, formset)

        original.refresh_from_db()
        self.assertEqual(original.order, 2)
        self.assertEqual(book.authorbook_set.count(), 2)
        self.assertEqual(book.authorbook_set.get(author=other).order, 3)

    def test_stale_add_is_rejected_when_the_link_already_exists(self):
        book = self.save_book_with_authors([self.author])
        original = book.authorbook_set.get()
        # An older page had no inline rows when another request added this author.
        formset = self.author_formset(book, [
            {'author': self.author.pk, 'role': 'primary', 'order': 9},
        ])

        self.assertFalse(formset.is_valid())
        self.assertTrue(formset.errors[0])
        self.assertEqual(book.authorbook_set.get().pk, original.pk)
        original.refresh_from_db()
        self.assertEqual(original.order, 2)

    def test_multiple_distinct_authors_are_saved(self):
        other = Author.objects.create(first_name='Jean', last_name='Martin')

        book = self.save_book_with_authors([self.author, other])

        self.assertEqual(book.authorbook_set.count(), 2)
        self.assertSetEqual(set(book.authors.all()), {self.author, other})

    def test_same_author_can_have_different_roles(self):
        book = Book(title='Un livre - Alice Dupont', pages_count=10,
                    pdf_file='books/example.pdf', cover='covers/existing.jpg')
        formset = self.author_formset(book, [
            {'author': self.author.pk, 'role': 'primary', 'order': 0},
            {'author': self.author.pk, 'role': 'translator', 'order': 1},
        ])

        self.save_author_formset(book, formset, change=False)

        self.assertSetEqual(
            set(book.authorbook_set.values_list('author_id', 'role', 'order')),
            {(self.author.pk, 'primary', 0), (self.author.pk, 'translator', 1)},
        )

    def test_deleting_the_last_author_does_not_immediately_recreate_it(self):
        book = self.save_book_with_authors([self.author])
        original = book.authorbook_set.get()
        formset = self.author_formset(book, [
            {'id': original.pk, 'author': self.author.pk, 'role': 'primary',
             'order': 2, 'DELETE': 'on'},
        ], initial_forms=1)

        self.save_author_formset(book, formset)

        self.assertFalse(book.authorbook_set.exists())
        self.assertTrue(Author.objects.filter(pk=self.author.pk).exists())

    def test_unchanged_admin_saves_preserve_the_same_link(self):
        book = self.save_book_with_authors([self.author])
        original = book.authorbook_set.get()
        for _ in range(3):
            formset = self.author_formset(book, [
                {'id': original.pk, 'author': self.author.pk,
                 'role': 'primary', 'order': 2},
            ], initial_forms=1)

            self.save_author_formset(book, formset)

            link = book.authorbook_set.get()
            self.assertEqual(link.pk, original.pk)
            self.assertEqual(link.order, 2)
