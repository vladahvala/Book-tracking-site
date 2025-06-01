import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django
django.setup()

import unittest
from unittest.mock import MagicMock
from django.test import RequestFactory
from app.patterns.search_handlers import (
    TitleSearchHandler,
    AuthorSearchHandler,
    GenreSearchHandler,
    SortSearchHandler
)
from app.models import Book

class SearchHandlerTests(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        # Створюємо тестові об'єкти книги
        self.book1 = Book.objects.create(
        book_title="Django Unchained",
        author="Tarantino",
        genre="Drama",
        Publication_Year=2012
       )

        self.book2 = Book.objects.create(
            book_title="Django for Beginners",
            author="William S. Vincent",
            genre="Education",
            Publication_Year=2018
        )

    def tearDown(self):
        Book.objects.all().delete()

    def build_chain(self):
        title_handler = TitleSearchHandler()
        author_handler = AuthorSearchHandler()
        genre_handler = GenreSearchHandler()
        sort_handler = SortSearchHandler()

        title_handler.set_next_handler(author_handler)\
                     .set_next_handler(genre_handler)\
                     .set_next_handler(sort_handler)

        return title_handler

    def test_title_search_handler(self):
        request = self.factory.get('/?q=Django&search_by=book_title')
        queryset = Book.objects.all()

        handler = self.build_chain()
        filtered = handler.handle(request, queryset)

        self.assertEqual(filtered.count(), 2)
        self.assertIn(self.book1, filtered)
        self.assertIn(self.book2, filtered)

    def test_author_search_handler(self):
        request = self.factory.get('/?q=William&search_by=author')
        queryset = Book.objects.all()

        handler = self.build_chain()
        filtered = handler.handle(request, queryset)

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.book2)

    def test_genre_search_handler(self):
        request = self.factory.get('/?q=Drama&search_by=genre')
        queryset = Book.objects.all()

        handler = self.build_chain()
        filtered = handler.handle(request, queryset)

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.book1)

    def test_sort_by_title(self):
        request = self.factory.get('/?sort=book_title')
        queryset = Book.objects.all()

        handler = self.build_chain()
        sorted_books = handler.handle(request, queryset)

        sorted_titles = list(sorted_books.values_list("book_title", flat=True))
        self.assertEqual(sorted_titles, sorted(sorted_titles))

if __name__ == '__main__':
    unittest.main()
