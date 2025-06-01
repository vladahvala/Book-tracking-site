import unittest
from unittest.mock import MagicMock
from app.patterns.strategies import SortByTitle, SortByRating, SortByAuthor, SortByYear

class TestSortStrategies(unittest.TestCase):
    def setUp(self):
        self.mock_qs = MagicMock()

    def test_sort_by_title(self):
        strategy = SortByTitle()
        strategy.sort(self.mock_qs)
        self.mock_qs.order_by.assert_called_once_with('book_title')

    def test_sort_by_rating(self):
        strategy = SortByRating()
        strategy.sort(self.mock_qs)
        self.mock_qs.order_by.assert_called_once_with('-rating')

    def test_sort_by_author(self):
        strategy = SortByAuthor()
        strategy.sort(self.mock_qs)
        self.mock_qs.order_by.assert_called_once_with('author')

    def test_sort_by_year(self):
        strategy = SortByYear()
        strategy.sort(self.mock_qs)
        self.mock_qs.order_by.assert_called_once_with('-year')

if __name__ == '__main__':
    unittest.main()
