# ==== PATTERN FACADE ====
# Structural 

from app.utils.pdf_utils import extract_pdf_details
from app.models import UserBook, Book
from app.views import find_similar_books


class BookDetailFacade:
    def __init__(self, book, user):
        self.book = book
        self.user = user
        self.user_book = None
        self.similar_books = []
        self.num_pages = None
        self.file_size_mb = None

    def build_details(self, all_books, confirm_download=False):
        self._set_user_book()
        self._set_similar_books(all_books)
        self._set_pdf_details(confirm_download)
        return self._build_context()

    def _set_user_book(self):
        if self.user and self.user.is_authenticated:
            self.user_book, _ = UserBook.objects.get_or_create(user=self.user, book=self.book)

    def _set_similar_books(self, all_books):
        self.similar_books = find_similar_books(self.book.book_title, all_books)

    def _set_pdf_details(self, confirm_download):
        try:
            if confirm_download:
                self.num_pages, self.file_size_mb = extract_pdf_details(self.book.file.path)
            else:
                self.num_pages, self.file_size_mb = None, None
        except MemoryError:
            self.num_pages, self.file_size_mb = None, None

    def _build_context(self):
        return {
            'book': self.book,
            'user_book': self.user_book,
            'similar_books': self.similar_books,
            'num_pages': self.num_pages,
            'file_size_mb': self.file_size_mb,
        }