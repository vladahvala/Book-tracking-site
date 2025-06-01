from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Book, UserBook, BookRequest, UserProfile, Comment

class ModelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

        self.book = Book.objects.create(
            book_title='Test Book',
            book_name='Test Book Name',
            book_annotation='Test annotation',
            author='Author Name',
            Category='Fiction',
            genre='Novel',
            ISBN='1234567890',
            Publication_Country='USA',
            Language='English',
            Publication_Year=2020
        )

    def test_book_creation_and_str(self):
        self.assertEqual(self.book.book_title, 'Test Book')
        self.assertEqual(str(self.book), 'Test Book')

    def test_userbook_creation_and_methods(self):
        user_book = UserBook.objects.create(user=self.user, book=self.book, status='reading', rating=4, review='Great book!')
        
        self.assertEqual(user_book.status, 'reading')
        self.assertEqual(user_book.get_status_display(), 'Reading')
        self.assertEqual(str(user_book), f"{self.book.book_title} - reading")
        
        # Перевірка методу get_state() повертає правильний клас
        state = user_book.get_state()
        self.assertEqual(state.__class__.__name__.lower(), 'readingstate')

    def test_userbook_update_review_rating(self):
        user_book = UserBook.objects.create(user=self.user, book=self.book, status='read')

        # Тепер методи add_review/add_rating точно працюватимуть
        user_book.add_review("New review")
        user_book.add_rating(5)

        self.assertEqual(user_book.review, "New review")
        self.assertEqual(user_book.rating, 5)


    def test_bookrequest_creation_and_str(self):
        br = BookRequest.objects.create(book_title='Requested Book', author='Request Author')
        self.assertEqual(str(br), f"Request for Requested Book by Request Author on {br.created_at}")

    def test_userprofile_creation_and_str(self):
        profile = UserProfile.objects.create(user=self.user, bio="User bio")
        self.assertEqual(str(profile), self.user.username)

    def test_comment_creation_and_str(self):
        comment = Comment.objects.create(book=self.book, name='Commenter', user=self.user, body='Nice book!')
        self.assertEqual(str(comment), f'{self.book.book_title} - Commenter')
        self.assertEqual(comment.body, 'Nice book!')
