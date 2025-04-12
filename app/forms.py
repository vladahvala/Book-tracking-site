from django import forms
from .models import UserBook
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder':'Введіть ім\'я...'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder':'Введіть пароль...'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder':'Підтвердіть пароль...'})


class UserBookForm(forms.ModelForm):
    class Meta:
        model = UserBook
        fields = ['status']
        labels = {
            'status': 'Change book status:',
            'rating': 'Rate this book:',
        }
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, '⭐' * i) for i in range(1, 6)])
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = UserBook
        fields = ['review']  # Лише поле відгуку
        labels = {
            'review': 'Write your review:',
        }
        widgets = {
            'review': forms.Textarea(attrs={'rows': 4, 'cols': 50}),  # Текстове поле для відгуку
        }