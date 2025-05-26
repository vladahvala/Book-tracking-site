# ==== PATTERN BUILDER ====
# Creational 

from collections import defaultdict
from ..models import Book

class CategoryBuilder:
    def __init__(self):
        self._categories = defaultdict(list)

    def initialize_from_books(self):
        """Ініціалізує категорії з усіх книг"""
        books = Book.objects.all()
        for book in books:
            if book.genre not in self._categories[book.Category]:
                self._categories[book.Category].append(book.genre)
        return self

    def add_subcategory(self, category_name, subcategory_name):
        """Додає підкатегорію до існуючої категорії"""
        if category_name in self._categories:
            if subcategory_name not in self._categories[category_name]:
                self._categories[category_name].append(subcategory_name)
            else:
                print(f"Subcategory '{subcategory_name}' already exists.")
        else:
            print(f"Category '{category_name}' doesn't exist.")
        return self

    def add_new_category(self, category_name, subcategory_names):
        """Додає нову категорію з підкатегоріями"""
        if category_name not in self._categories:
            self._categories[category_name] = subcategory_names
        else:
            print(f"Category '{category_name}' already exists.")
        return self

    def build(self):
        """Фіналізує побудову — повертає словник категорій"""
        return dict(self._categories)
