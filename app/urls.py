from django.urls import path
from app.views import *
from . import views

urlpatterns = [
    path('login/', views.loginUser, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerUser, name="register"),

    path('', search_books, name='search_books'),
    path('genres/', views.genres, name='genres'),
    path('book/<int:pk>/', book_detail, name='book_detail'),
    path('trends/', book_stats, name='trends'),
    path('about/', about, name='about'),
    path('profile/', views.profile, name='profile'),
    path('search/', views.search_certain_book, name='search_certain_book'),
    path('book/<int:pk>/comment/', AddCommentView.as_view(), name='add_comment'),
]
