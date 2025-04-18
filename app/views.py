from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import F
from .models import Book
from .utils import find_similar_books
from django.shortcuts import render, get_object_or_404
from .models import Book, Comment
from .utils import find_similar_books
import os
import fitz  # PyMuPDF
from django.db.models import Count
import plotly.graph_objs as go
from .models import Book, UserBook
from .forms import UserBookForm, CustomUserCreationForm
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from abc import ABC, abstractmethod
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
import fitz
import os
import plotly.graph_objs as go
from .models import Book, UserBook
from .forms import UserBookForm
from .observer import BookStatistics, BookRecommendations

def loginUser(request):
    page = 'login'
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('profile')

    return render(request, 'login_register.html', {'page':page})

def logoutUser(request):
    logout(request)
    return redirect('login')

def registerUser(request):
    page = 'register'
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])  # встановлення пароля
            user.save()  # збереження користувача в базу даних

            # Тепер ми можемо аутентифікувати користувача з новим паролем
            user = authenticate(request, username=user.username, password=request.POST['password1'])
            
            if user is not None:
                login(request, user)  # авторизація користувача
                return redirect('main')  # перенаправлення на головну сторінку

    context = {'form': form, 'page': page}
    return render(request, 'login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

class AddCommentView(CreateView):
    model = Comment
    template_name='add_comment.html'
    fields='__all__'




# ==== PATTERN STRATEGY ====

class BookSortStrategy(ABC):
    @abstractmethod
    def sort(self, query_set):
        pass

class SortByTitle(BookSortStrategy):
    def sort(self, query_set):
        return query_set.order_by('book_title')

class SortByRating(BookSortStrategy):
    def sort(self, query_set):
        return query_set.order_by('-rating')

class SortByAuthor(BookSortStrategy):
    def sort(self, query_set):
        return query_set.order_by('author')
    

# ==== PATTERN FACTORY ====

class SortStrategyFactory:
    @staticmethod
    def create_strategy(sort_by: str) -> BookSortStrategy:
        if sort_by == 'rating':
            return SortByRating()
        elif sort_by == 'author':
            return SortByAuthor()
        else:
            return SortByTitle()


# ==== VIEWS ====

def genres(request):
    categories = {
        'Business Literature': ['Business Literature', 'Career & HR', 'Marketing & PR', 'Finance', 'Economics'],
        'Detectives & Thrillers': ['Action', 'Detectives', 'Humorous & Women,\'s Detectives', 'Historical Detective', 
                                   'Classic Detective', 'Crime Detective', 'Hard-Boiled Detective', 'Political Detective', 
                                   'Police Detective', 'Maniac Stories', 'Soviet Detective', 'Thriller', 'Espionage Detective'],
        'Nonfiction Literature': ['Biographies & Memoirs', 'Military Documentary & Analysis', 'Military Science', 'Geography & Travel Notes', 'General Nonfiction', 'Journalism & Publicism'],
        'Home & Family': ['Cars & Traffic Rules', 'Martial Arts & Sports', 'Pets', 'Home Economics', 'Health', 'Cooking', 'Entertainment'],                           
        'Art, Art Studies & Design': ['Painting, Albums, Illustrated Catalogs', 'Art & Design', 'Art Criticism', 'Cinema & Film', 'Music', 'Theatre', 'Sculpture & Architecture'],
        'Computers & Internet': ['Foreign Computer Literature', 'Computer Hardware & Digital Signal Processing', 'Operating Systems, Networks & Internet', 
                                 'Programming, Software & Databases', 'Computer Tutorials & Guides'],
        'Children’s Literature': ['General Children\'s Literature', 'Educational Literature for Children', 'Thrilling Literature for Children', 
                                 'Games & Exercises for Children', 'World Folk Tales'],
        'Romance Novels': ['Historical Romance', 'Short Romance Stories', 'Romantic Fantasy', 
                                 'Romantic Thrillers', 'Contemporary Romance'],
        'Science & Education': ['Alternative Medicine', 'Alternative Sciences & Theories', 'Biology, Biophysics & Biochemistry', 
                                 'Military History', 'Law & Government'],
        'Poetry': ['Classical foreign poetry', 'Song lyrics poetry', 'Modern foreign poetry'],        
        'Adventure': ['Adventure novel', 'Adventures', 'Modern world adventures', 
                                 'Nature and animals', 'Maritime adventures'],
        'Prose': ['Gothic novel', 'Classical prose of the 19th century', 'War prose', 
                                 'Phantasmagoria, absurdist prose', 'Epistolary prose'],                        
        'Science Fiction and Fantasy': ['Heroic fantasy', 'Cyberpunk', 'Mythological fantasy', 
                                 'Post-apocalypse', 'Slavic fantasy', 'Horror', 'Steampunk', 
                                 'Fantasy', 'Epic science fiction', 'Modern fairy tale'],    
        'Humor': ['Jokes', 'Satire', 'Humor'], 
    }

    books_by_subcategory = []
    for subcategory in Book.objects.values_list('genre', flat=True).distinct():
        books = list(Book.objects.filter(genre=subcategory).values('id', 'book_title', 'author'))
        books_by_subcategory.append((subcategory, books))

    return render(request, 'genres.html', {
        'categories': categories,
        'books_by_subcategory': books_by_subcategory,
    })

def search_certain_book(request):
    query = request.GET.get('q')
    sort_by = request.GET.get('sort', 'book_title')
    results = []

    if query:
        queryset = Book.objects.filter(
            Q(book_title__icontains=query) | Q(author__icontains=query)
        )
        sort_strategy = SortStrategyFactory.create_strategy(sort_by)
        results = sort_strategy.sort(queryset)

    return render(request, 'search_results.html', {
        'query': query,
        'results': results,
        'sort_by': sort_by,
    })


def search_books(request):
    query = request.GET.get('query', '')
    similar_books = find_similar_books(query, Book.objects.all())

    return render(request, 'recommendations.html', {
        'query': query,
        'similar_books': similar_books,
    })

def extract_pdf_details(pdf_path):
    document = fitz.open(pdf_path)
    num_pages = document.page_count
    file_size = os.path.getsize(pdf_path) / (1024 * 1024)
    return num_pages, file_size

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)

    session_key = request.session.session_key
    if not session_key:
        request.session.create()

    user_book, _ = UserBook.objects.get_or_create(session_key=session_key, book=book)

    all_books = Book.objects.exclude(pk=pk)
    similar_books = find_similar_books(book.book_title, all_books)
    num_pages, file_size = extract_pdf_details(book.file.path)

    if request.method == 'POST':
        status = request.POST.get('status')
        if not request.session.session_key:
            request.session.create()

        user_book, _ = UserBook.objects.get_or_create(session_key=session_key, book=book)

        if status == 'unread':
            user_book.delete()
        else:
            user_book.status = status
            user_book.save()

        return redirect('book_detail', pk=pk)

    return render(request, 'book_detail.html', {
        'book': book,
        'similar_books': similar_books,
        'num_pages': num_pages,
        'file_size_mb': file_size,
        'user_book': user_book,
    })

def book_stats(request):
    data = Book.objects.values('Publication_Year', 'Category').annotate(count=Count('id'))
    categories = sorted(set(item['Category'] for item in data))
    years = sorted(set(item['Publication_Year'] for item in data))

    category_counts_by_year = {cat: [0] * len(years) for cat in categories}
    for item in data:
        category_counts_by_year[item['Category']][years.index(item['Publication_Year'])] = item['count']

    fig = go.Figure()
    for cat in categories:
        fig.add_trace(go.Bar(x=years, y=category_counts_by_year[cat], name=cat))

    fig.update_layout(
        barmode='stack',
        title='Stacked Vertical Bar Chart of Book Categories by Publication Year',
        xaxis_title='Publication Year',
        yaxis_title='Frequency',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='gray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='gray')

    return render(request, 'trend.html', {
        'fig_html': fig.to_html(full_html=False),
    })

def about(request):
    return render(request, 'about.html')

@login_required(login_url='login')
def profile(request):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()

    if request.method == 'POST':
        book_id = request.POST.get('book')
        action = request.POST.get('action')
        status = request.POST.get('status')
        rating = request.POST.get('rating')

        if book_id:
            try:
                book = Book.objects.get(id=book_id)
                user_book = UserBook.objects.get(session_key=session_key, book=book)

                if action == 'update_status' and status:
                    if status == 'unread':
                        user_book.delete()
                        return redirect('profile')
                    else:
                        user_book.status = status
                        user_book.save()
                elif action == 'update_rating' and rating:
                    user_book.rating = int(rating)
                    user_book.save()
                elif action == 'update_review':
                    review = request.POST.get('review')
                    user_book.review = review
                    user_book.save()

                return redirect('profile')
            except (Book.DoesNotExist, UserBook.DoesNotExist):
                pass

    reading_page = request.GET.get('reading_page', 1)
    read_page = request.GET.get('read_page', 1)
    planning_page = request.GET.get('planning_page', 1)

    reading_books = UserBook.objects.filter(status='reading', session_key=session_key)
    read_books = UserBook.objects.filter(status='read', session_key=session_key)
    planning_books = UserBook.objects.filter(status='planning', session_key=session_key)

    reading_paginator = Paginator(reading_books, 6)
    read_paginator = Paginator(read_books, 6)
    planning_paginator = Paginator(planning_books, 6)

    return render(request, 'profile.html', {
        'user_books_reading': reading_paginator.get_page(reading_page),
        'user_books_read': read_paginator.get_page(read_page),
        'user_books_planning': planning_paginator.get_page(planning_page),
        'form': UserBookForm(),
    })

@login_required(login_url='login')
def book_status(request, pk):
    book = get_object_or_404(Book, pk=pk)
    session_key = request.session.session_key
    if not session_key:
        request.session.create()

    user_book, _ = UserBook.objects.get_or_create(session_key=session_key, book=book)

    # Додаємо спостерігачів до UserBook
    statistics_observer = BookStatistics()
    recommendations_observer = BookRecommendations()
    user_book.add_observer(statistics_observer)
    user_book.add_observer(recommendations_observer)


    if request.method == 'POST':
        form = UserBookForm(request.POST, instance=user_book)
        rating = request.POST.get('rating')

        if form.is_valid():
            if form.cleaned_data['status'] == 'unread':
                user_book.delete()
            else:
                form.save()
                if rating:
                    user_book.rating = int(rating)
                    user_book.save()
            return redirect('profile')
    else:
        form = UserBookForm(instance=user_book)

    return render(request, 'app/book_detail.html', {
        'book': book,
        'form': form,
    })