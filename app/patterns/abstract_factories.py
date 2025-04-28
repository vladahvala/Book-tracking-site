# ==== PATTERN ABSTRACT FACTORY ==== 
# Creational 

from ..models import Book

class DynamicCategoryFactory:
    def __init__(self):
        self.categories = {}  # Категорії і підкатегорії
        self._initialize_categories()

    def _initialize_categories(self):
        """Ініціалізація категорій та підкатегорій з даних книги"""
        books = Book.objects.all()
        for book in books:
            # Перевірка наявності категорії
            if book.Category not in self.categories:
                self.categories[book.Category] = []
            # Додаємо підкатегорію (genre) тільки якщо її ще немає в категорії
            if book.genre not in self.categories[book.Category]:
                self.categories[book.Category].append(book.genre)

    def add_subcategory(self, category_name, subcategory_name):
        """Додати нову підкатегорію до існуючої категорії"""
        if category_name in self.categories:
            if subcategory_name not in self.categories[category_name]:
                self.categories[category_name].append(subcategory_name)
                # Можна також додати підкатегорію в базу даних для нових книг, якщо потрібно
            else:
                print(f"Subcategory '{subcategory_name}' already exists.")
        else:
            print(f"Category '{category_name}' doesn't exist.")
    
    def add_new_category(self, category_name, subcategory_names):
        """Додати нову категорію з підкатегоріями"""
        if category_name not in self.categories:
            self.categories[category_name] = subcategory_names
        else:
            print(f"Category '{category_name}' already exists.")



