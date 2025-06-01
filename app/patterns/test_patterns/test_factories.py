import unittest
from app.patterns.factories import SortStrategyFactory
from app.patterns.strategies import SortByRating, SortByAuthor, SortByTitle, SortByYear

class TestSortStrategyFactory(unittest.TestCase):
    def test_create_strategy_rating(self):
        strategy = SortStrategyFactory.create_strategy('rating')
        self.assertIsInstance(strategy, SortByRating)

    def test_create_strategy_author(self):
        strategy = SortStrategyFactory.create_strategy('author')
        self.assertIsInstance(strategy, SortByAuthor)

    def test_create_strategy_title(self):
        strategy = SortStrategyFactory.create_strategy('title')
        self.assertIsInstance(strategy, SortByTitle)

    def test_create_strategy_year(self):
        strategy = SortStrategyFactory.create_strategy('year')
        self.assertIsInstance(strategy, SortByYear)

    def test_create_strategy_invalid_key_returns_default(self):
        strategy = SortStrategyFactory.create_strategy('unknown')
        self.assertIsInstance(strategy, SortByTitle)

if __name__ == '__main__':
    unittest.main()
