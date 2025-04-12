from django import forms
from .models import UserBook

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