import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django
django.setup()

import unittest
from unittest.mock import MagicMock, patch
from django.http import HttpRequest
from django.contrib.auth.models import AnonymousUser
from app.patterns.handlers import LoginHandler, RegisterHandler

class TestLoginHandler(unittest.TestCase):
    def setUp(self):
        self.handler = LoginHandler()
        self.request = MagicMock(spec=HttpRequest)
        self.request.method = 'POST'
        self.request.POST = {'username': 'user', 'password': 'pass'}
        self.request.user = AnonymousUser()

    @patch('app.patterns.handlers.authenticate')
    @patch('app.patterns.handlers.login')
    @patch('app.patterns.handlers.redirect')
    def test_process_post_success(self, mock_redirect, mock_login, mock_authenticate):
        mock_user = MagicMock()
        mock_authenticate.return_value = mock_user
        mock_redirect.return_value = 'redirected'

        response = self.handler.process_post(self.request)

        mock_authenticate.assert_called_once_with(self.request, username='user', password='pass')
        mock_login.assert_called_once_with(self.request, mock_user)
        mock_redirect.assert_called_once_with('profile')
        self.assertEqual(response, 'redirected')

    @patch('app.patterns.handlers.authenticate')
    @patch('app.patterns.handlers.render')
    def test_process_post_fail(self, mock_render, mock_authenticate):
        mock_authenticate.return_value = None
        mock_render.return_value = 'rendered'

        response = self.handler.process_post(self.request)

        mock_authenticate.assert_called_once()
        mock_render.assert_called_once_with(self.request, 'login_register.html', {'page': 'login', 'error': 'Невірні дані'})
        self.assertEqual(response, 'rendered')

    @patch('app.patterns.handlers.render')
    def test_render_form(self, mock_render):
        mock_render.return_value = 'rendered_form'
        response = self.handler.render_form(self.request)

        mock_render.assert_called_once_with(self.request, 'login_register.html', {'page': 'login'})
        self.assertEqual(response, 'rendered_form')


class TestRegisterHandler(unittest.TestCase):
    def setUp(self):
        self.handler = RegisterHandler()
        self.request = MagicMock(spec=HttpRequest)
        self.request.method = 'POST'
        self.request.POST = {'username': 'newuser', 'password1': 'pass123', 'password2': 'pass123'}
        self.request.user = AnonymousUser()

    @patch('app.patterns.handlers.CustomUserCreationForm')
    @patch('app.patterns.handlers.authenticate')
    @patch('app.patterns.handlers.login')
    @patch('app.patterns.handlers.redirect')
    def test_process_post_valid_form(self, mock_redirect, mock_login, mock_authenticate, mock_form_cls):
        mock_form = MagicMock()
        mock_form.is_valid.return_value = True
        mock_form.cleaned_data = {'password1': 'pass123'}

        mock_user = MagicMock()
        mock_user.username = 'newuser'  # <--- ВАЖЛИВА ПРАВКА
        mock_form.save.return_value = mock_user

        mock_form_cls.return_value = mock_form

        mock_authenticate.return_value = mock_user
        mock_redirect.return_value = 'redirected'

        response = self.handler.process_post(self.request)

        mock_form.is_valid.assert_called_once()
        mock_form.save.assert_called_once_with(commit=False)
        mock_user.set_password.assert_called_once_with('pass123')
        mock_user.save.assert_called_once()
        mock_authenticate.assert_called_once_with(self.request, username='newuser', password='pass123')
        mock_login.assert_called_once_with(self.request, mock_user)
        mock_redirect.assert_called_once_with('main')

        self.assertEqual(response, 'redirected')


    @patch('app.patterns.handlers.CustomUserCreationForm')
    @patch('app.patterns.handlers.render')
    def test_process_post_invalid_form(self, mock_render, mock_form_cls):
        mock_form = MagicMock()
        mock_form.is_valid.return_value = False
        mock_form_cls.return_value = mock_form
        mock_render.return_value = 'rendered'

        response = self.handler.process_post(self.request)

        mock_form.is_valid.assert_called_once()
        mock_render.assert_called_once_with(self.request, 'login_register.html', {'form': mock_form, 'page': 'register'})
        self.assertEqual(response, 'rendered')

    @patch('app.patterns.handlers.CustomUserCreationForm')
    @patch('app.patterns.handlers.render')
    def test_render_form(self, mock_render, mock_form_cls):
        mock_form = MagicMock()
        mock_form_cls.return_value = mock_form
        mock_render.return_value = 'rendered_form'

        response = self.handler.render_form(self.request)

        mock_render.assert_called_once_with(self.request, 'login_register.html', {'form': mock_form, 'page': 'register'})
        self.assertEqual(response, 'rendered_form')


if __name__ == '__main__':
    unittest.main()
