from django.urls import path
from app.views import *
from . import views

urlpatterns = [
    path('', search_books, name='search_books'),
    path('book/<int:pk>/', book_detail, name='book_detail'),
    path('trends/', book_stats, name='trends'),
    path('about/', about, name='about'),
    path('profile/', views.profile, name='profile')
]
