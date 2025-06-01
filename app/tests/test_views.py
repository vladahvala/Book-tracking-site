import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock

from ..models import Book, BookRequest, Comment, UserBook, UserProfile

class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.book = Book.objects.create(
            id=1, book_title='Test Book', author='Author', genre='Fiction', 
            Publication_Year=2020, file='testfile.pdf'
        )
        self.user_book = UserBook.objects.create(user=self.user, book=self.book, status='reading')
        self.user_profile = UserProfile.objects.create(user=self.user)
    
    def test_about_view(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about.html')

    def test_submit_book_request_post(self):
        response = self.client.post(reverse('submit_book_request'), {
            'book_title': 'New Book',
            'author': 'New Author'
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'message': 'Thank you for your request! We will add the book soon.'})
        self.assertTrue(BookRequest.objects.filter(book_title='New Book').exists())
    
    def test_submit_book_request_get_invalid(self):
        response = self.client.get(reverse('submit_book_request'))
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'message': 'Invalid request'})

    def test_logout_user_redirects(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    def test_login_required_custom_decorator_redirects(self):
        # При спробі зайти на профіль без логіну має бути редірект
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_profile_view_logged_in(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertIn('user_profile', response.context)
        self.assertIn('reading_books_page', response.context)

    def test_book_detail_get(self):
        self.client.login(username='testuser', password='12345')
        url = reverse('book_detail', kwargs={'pk': self.book.id})
        with patch('app.views.PDFProxy') as mock_proxy, \
            patch('app.views.BookDetailFacade') as mock_facade:
            mock_proxy.return_value.is_too_large.return_value = False
            mock_proxy.return_value.file_size = 1.5

            mock_facade_instance = mock_facade.return_value
            mock_facade_instance.build_details.return_value = {
                'book': self.book,
                'num_pages': 100,
                'file_size': 1.5,
            }
            mock_facade_instance.num_pages = 100
            mock_facade_instance.file_size_mb = 1.5

            response = self.client.get(url)

            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'book_detail.html')
            self.assertIn('book', response.context)
            self.assertEqual(response.context['book'], self.book)


    def test_delete_comment_authorized(self):
        self.client.login(username='testuser', password='12345')
        comment = Comment.objects.create(book=self.book, user=self.user, body='Test comment', name='testuser')
        url = reverse('delete_comment', kwargs={'comment_id': comment.id})
        response = self.client.post(url)
        self.assertJSONEqual(response.content, {'success': True})
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())

    def test_delete_comment_unauthorized(self):
        other_user = User.objects.create_user(username='other', password='12345')
        comment = Comment.objects.create(book=self.book, user=other_user, body='Other comment', name='other')
        self.client.login(username='testuser', password='12345')
        url = reverse('delete_comment', kwargs={'comment_id': comment.id})
        response = self.client.post(url)
        self.assertJSONEqual(response.content, {'success': False, 'error': 'You are not authorized to delete this comment.'})
        self.assertTrue(Comment.objects.filter(id=comment.id).exists())

    def test_search_books_view(self):
        url = reverse('search_books')
        response = self.client.get(url, {'query': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recommendations.html')
        self.assertIn('similar_books', response.context)

    
    def test_book_detail_pdf_too_large(self):
        self.client.login(username='testuser', password='12345')
        url = reverse('book_detail', kwargs={'pk': self.book.id})

        with patch('app.views.PDFProxy') as mock_proxy, \
            patch('app.views.BookDetailFacade') as mock_facade:

            # Налаштовуємо мок, щоб PDF вважався занадто великим
            mock_proxy.return_value.is_too_large.return_value = True
            mock_proxy.return_value.file_size = 25.5  # наприклад 25.5 MB

            # Налаштовуємо мок фасаду, щоб build_details повертав словник контексту
            mock_facade.return_value.build_details.return_value = {
                'book': self.book,
                'num_pages': 100,
                'file_size': 25.5,
            }


            response = self.client.get(url)

            # Перевіряємо статус відповіді (200 - OK)
            self.assertEqual(response.status_code, 200)

            # Перевіряємо, що контекст містить ключі, які ти додаєш вручну
            self.assertIn('is_large_file', response.context)
            self.assertIn('file_size', response.context)
            self.assertIn('confirm_download', response.context)

            # Перевірка, що PDFProxy.is_too_large() викликався
            mock_proxy.return_value.is_too_large.assert_called_once()


        