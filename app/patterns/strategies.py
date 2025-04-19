# ==== PATTERN STRATEGY ====
# Behavioral

from abc import ABC, abstractmethod

class BookSortStrategy(ABC):
    @abstractmethod
    def sort(self, query_set):
        pass

class SortByTitle(BookSortStrategy):
    def sort(self, query_set):
        return query_set.order_by('book_title')

class SortByRating(BookSortStrategy):
    def sort(self, query_set):
        return query_set.order_by('-rating')

class SortByAuthor(BookSortStrategy):
    def sort(self, query_set):
        return query_set.order_by('author')

class SortByYear(BookSortStrategy):
    def sort(self, query_set):
        return query_set.order_by('-year')
