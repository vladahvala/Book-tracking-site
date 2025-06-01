import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django
django.setup()

import unittest
from django.contrib.auth.models import User
from app.models import UserBook, Book
from app.patterns.states import UnreadState, PlanningState, ReadingState, ReadState

class BookStateTests(unittest.TestCase):

    def setUp(self):
        # Create a user to satisfy UserBook's user FK if required
        self.user = User.objects.create_user(username='testuser', password='12345')

        # Create a book to satisfy UserBook's book FK
        self.book = Book.objects.create(
            book_title='Sample Book',
            author='Sample Author',
            genre='Fiction',
            Publication_Year=2020,
            file='sample.pdf',  # adjust if your file field requires an actual file
        )

        # Create UserBook with required FKs
        self.user_book = UserBook.objects.create(
            status="unread",
            user=self.user,
            book=self.book,
        )

    def tearDown(self):
        UserBook.objects.all().delete()
        Book.objects.all().delete()
        User.objects.all().delete()

    def test_unread_state_update_status(self):
        state = UnreadState()
        state.update_status(self.user_book, "planning")
        self.user_book.refresh_from_db()
        self.assertEqual(self.user_book.status, "planning")


    def test_unread_state_review_not_supported(self):
        state = UnreadState()
        with self.assertRaises(NotImplementedError):
            state.add_review(self.user_book, "Good book")

    def test_planning_state_review_not_supported(self):
        state = PlanningState()
        with self.assertRaises(NotImplementedError):
            state.add_review(self.user_book, "Planning to read")

    def test_reading_state_rating_not_supported(self):
        state = ReadingState()
        with self.assertRaises(NotImplementedError):
            state.add_rating(self.user_book, 4)

    def test_read_state_allows_review_and_rating(self):
        state = ReadState()
        state.add_review(self.user_book, "Amazing book!")
        state.add_rating(self.user_book, 5)

        self.user_book.refresh_from_db()
        self.assertEqual(self.user_book.review, "Amazing book!")
        self.assertEqual(self.user_book.rating, 5)

    def test_read_state_update_status(self):
        state = ReadState()
        state.update_status(self.user_book, "archived")
        self.user_book.refresh_from_db()
        self.assertEqual(self.user_book.status, "archived")
