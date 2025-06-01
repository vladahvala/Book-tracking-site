import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django
django.setup()

import unittest
from unittest.mock import MagicMock, patch
from app.views import BookDetailFacade


class TestBookDetailFacade(unittest.TestCase):
    def setUp(self):
        self.book = MagicMock()
        self.book.book_title = 'Test Book'
        self.book.file.path = '/fake/path/to/book.pdf'
        self.user = MagicMock()
        self.user.is_authenticated = True

        book1 = MagicMock()
        book1.book_title = 'Book1'
        book2 = MagicMock()
        book2.book_title = 'Book2'
        self.all_books = [book1, book2]

    @patch('fitz.open')
    @patch('os.path.getsize', return_value=5 * 1024 * 1024)
    @patch('app.patterns.facade.extract_pdf_details')
    @patch('app.patterns.facade.find_similar_books')
    @patch('app.models.UserBook.objects.get_or_create')
    def test_build_details_confirm_download_true(self, mock_get_or_create, mock_find_similar, mock_extract_pdf, mock_getsize, mock_fitz_open):
        mock_fitz_open.return_value = MagicMock()
        mock_get_or_create.return_value = (MagicMock(), True)
        mock_find_similar.return_value = ['Similar1', 'Similar2']
        mock_extract_pdf.return_value = (100, 1.5)

        facade = BookDetailFacade(self.book, self.user)
        context = facade.build_details(self.all_books, confirm_download=True)

        mock_get_or_create.assert_called_once()
        mock_find_similar.assert_called_once_with(self.book.book_title, self.all_books)
        mock_extract_pdf.assert_called_once_with(self.book.file.path)

        self.assertEqual(context['num_pages'], 100)
        self.assertEqual(context['file_size_mb'], 1.5)

    @patch('app.models.UserBook.objects.get_or_create')
    @patch('app.patterns.facade.find_similar_books')
    def test_build_details_confirm_download_false(self, mock_find_similar, mock_get_or_create):
        mock_get_or_create.return_value = (MagicMock(), True)
        mock_find_similar.return_value = ['Similar1', 'Similar2']

        facade = BookDetailFacade(self.book, self.user)
        context = facade.build_details(self.all_books, confirm_download=False)

        mock_find_similar.assert_called_once_with(self.book.book_title, self.all_books)
        self.assertIsNone(context['num_pages'])
        self.assertIsNone(context['file_size_mb'])

    @patch('fitz.open')
    @patch('os.path.getsize', return_value=5 * 1024 * 1024)
    @patch('app.models.UserBook.objects.get_or_create')
    @patch('app.patterns.facade.extract_pdf_details')
    @patch('app.patterns.facade.find_similar_books')
    def test_build_details_memory_error(
        self,
        mock_find_similar,
        mock_extract_pdf,
        mock_get_or_create,
        mock_getsize,
        mock_fitz_open
    ):
        mock_get_or_create.return_value = (MagicMock(), True)
        mock_find_similar.return_value = ["similar_book"]
        mock_extract_pdf.side_effect = MemoryError("Simulated memory error")

        facade = BookDetailFacade(self.book, self.user)
        context = facade.build_details(self.all_books, confirm_download=True)

        self.assertIsNone(context['num_pages'])
        self.assertIsNone(context['file_size_mb'])

    def test_set_user_book_not_authenticated(self):
        user = MagicMock()
        user.is_authenticated = False

        facade = BookDetailFacade(self.book, user)
        facade._set_user_book()

        self.assertIsNone(facade.user_book)


if __name__ == '__main__':
    unittest.main()
