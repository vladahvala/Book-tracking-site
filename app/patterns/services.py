# ==== PATTERN BUILDER ====

from app.utils.pdf_utils import extract_pdf_details
from app.models import UserBook
from app.views import find_similar_books

class BookDetailBuilder:
    def __init__(self, book, session_key):
        self.book = book
        self.session_key = session_key
        self.user_book = None
        self.similar_books = []
        self.num_pages = 0
        self.file_size = 0

    def set_user_book(self):
        self.user_book, _ = UserBook.objects.get_or_create(session_key=self.session_key, book=self.book)
        return self

    def set_similar_books(self, all_books):
        self.similar_books = find_similar_books(self.book.book_title, all_books)
        return self

    def set_pdf_details(self):
        self.num_pages, self.file_size = extract_pdf_details(self.book.file.path)
        return self

    def build(self):
        return {
            'book': self.book,
            'similar_books': self.similar_books,
            'num_pages': self.num_pages,
            'file_size_mb': self.file_size,
            'user_book': self.user_book,
        }
