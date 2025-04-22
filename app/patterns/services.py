# ==== PATTERN BUILDER ====
# Creational 

from app.utils.pdf_utils import extract_pdf_details
from app.models import UserBook
from app.views import find_similar_books

class BookDetailBuilder:
    def __init__(self, book, user):
        self.book = book
        self.user = user  # Замість session_key, передаємо користувача
        self.user_book = None
        self.similar_books = []
        self.num_pages = 0
        self.file_size = 0

    def set_user_book(self):
        # Тепер використовуємо користувача замість session_key
        self.user_book, _ = UserBook.objects.get_or_create(user=self.user, book=self.book)
        return self

    def set_similar_books(self, all_books):
        self.similar_books = find_similar_books(self.book.book_title, all_books)
        return self

    def set_pdf_details(self):
        try:
            self.num_pages, self.file_size = extract_pdf_details(self.book.file.path)
        except MemoryError:
            self.num_pages, self.file_size = None, None
        return self

    def build(self):
        return {
            'book': self.book,
            'similar_books': self.similar_books,
            'num_pages': self.num_pages,
            'file_size_mb': self.file_size,
            'user_book': self.user_book,
        }