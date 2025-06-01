import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django
django.setup()

import unittest
from collections import defaultdict
from unittest.mock import patch, MagicMock
from app.patterns.genre_builder import CategoryBuilder

class TestCategoryBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = CategoryBuilder()

    @patch('app.models.Book.objects.all')
    def test_initialize_from_books(self, mock_all):
        # Підготовка мок-об'єктів книг
        book1 = MagicMock()
        book1.Category = 'Fiction'
        book1.genre = 'Fantasy'
        book2 = MagicMock()
        book2.Category = 'Fiction'
        book2.genre = 'Adventure'
        book3 = MagicMock()
        book3.Category = 'Non-fiction'
        book3.genre = 'History'
        
        mock_all.return_value = [book1, book2, book3]

        builder = self.builder.initialize_from_books()
        categories = builder.build()

        self.assertIn('Fiction', categories)
        self.assertIn('Non-fiction', categories)
        self.assertCountEqual(categories['Fiction'], ['Fantasy', 'Adventure'])
        self.assertEqual(categories['Non-fiction'], ['History'])

    def test_add_subcategory_existing_category(self):
        self.builder._categories = defaultdict(list, {'Fiction': ['Fantasy']})
        builder = self.builder.add_subcategory('Fiction', 'Adventure')
        categories = builder.build()

        self.assertIn('Adventure', categories['Fiction'])
        self.assertEqual(len(categories['Fiction']), 2)

    def test_add_subcategory_non_existing_category(self):
        # Підмінимо print, щоб перевірити виклик
        with patch('builtins.print') as mock_print:
            builder = self.builder.add_subcategory('NonExistent', 'Mystery')
            mock_print.assert_called_with("Category 'NonExistent' doesn't exist.")

    def test_add_subcategory_duplicate(self):
        self.builder._categories = defaultdict(list, {'Fiction': ['Fantasy']})
        with patch('builtins.print') as mock_print:
            builder = self.builder.add_subcategory('Fiction', 'Fantasy')
            mock_print.assert_called_with("Subcategory 'Fantasy' already exists.")

    def test_add_new_category_new(self):
        builder = self.builder.add_new_category('Sci-Fi', ['Dystopia', 'Space Opera'])
        categories = builder.build()

        self.assertIn('Sci-Fi', categories)
        self.assertCountEqual(categories['Sci-Fi'], ['Dystopia', 'Space Opera'])

    def test_add_new_category_existing(self):
        self.builder._categories = defaultdict(list, {'Fiction': ['Fantasy']})
        with patch('builtins.print') as mock_print:
            builder = self.builder.add_new_category('Fiction', ['Adventure'])
            mock_print.assert_called_with("Category 'Fiction' already exists.")

    def test_build_returns_dict(self):
        self.builder._categories = defaultdict(list, {'Fiction': ['Fantasy']})
        result = self.builder.build()
        self.assertIsInstance(result, dict)
        self.assertEqual(result['Fiction'], ['Fantasy'])

if __name__ == '__main__':
    unittest.main()
