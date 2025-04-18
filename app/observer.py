# observer.py

# Базовий клас Observer
class Observer:
    def update(self, book):
        raise NotImplementedError("Метод 'update' має бути реалізований в підкласах.")

# Спостерігач для статистики
class BookStatistics(Observer):
    def update(self, book):
        print(f"Оновлення статистики для книги: {book.book_title}. Статус: {book.status}.")
        # Можна оновити статистику в базі даних чи кеші

# Спостерігач для рекомендацій
class BookRecommendations(Observer):
    def update(self, book):
        print(f"Оновлення рекомендацій на основі книги '{book.book_title}'. Новий статус: {book.status}.")
        # Можна генерувати нові рекомендації на основі зміни статусу книги
