# ==== PATTERN TEMPLATE METHOD ====
# Behavioral

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from ..forms import CustomUserCreationForm  # якщо є
# або імпортуєш з іншого місця, де вона у тебе визначена

class BaseAuthHandler:
    def handle(self, request):
        if request.method == 'POST':
            return self.process_post(request)
        return self.render_form(request)

    def process_post(self, request):
        raise NotImplementedError

    def render_form(self, request):
        raise NotImplementedError


class LoginHandler(BaseAuthHandler):
    def process_post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        return render(request, 'login_register.html', {'page': 'login', 'error': 'Невірні дані'})

    def render_form(self, request):
        return render(request, 'login_register.html', {'page': 'login'})


class RegisterHandler(BaseAuthHandler):
    def process_post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()

            user = authenticate(request, username=user.username, password=request.POST['password1'])
            if user is not None:
                login(request, user)
                return redirect('main')
        return render(request, 'login_register.html', {'form': form, 'page': 'register'})

    def render_form(self, request):
        form = CustomUserCreationForm()
        return render(request, 'login_register.html', {'form': form, 'page': 'register'})
