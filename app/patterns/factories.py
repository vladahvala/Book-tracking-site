# ==== PATTERN FACTORY METHOD ====
# Creational 

from .strategies import SortByRating, SortByAuthor, SortByTitle, SortByYear

class SortStrategyFactory:
    @staticmethod
    def create_strategy(sort_by: str):
        strategies = {
            'rating': SortByRating,
            'author': SortByAuthor,
            'title': SortByTitle,
            'year': SortByYear,
        }
        return strategies.get(sort_by, SortByTitle)()
