from django.shortcuts import render, get_object_or_404, redirect
from .utils import find_similar_books
from .models import Book, UserBook, Comment
from .forms import UserBookForm, CustomUserCreationForm

import os
import fitz  # PyMuPDF
from django.db.models import Count
import plotly.graph_objs as go
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q, Count
from django.views.generic.edit import CreateView
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .patterns.factories import SortStrategyFactory
from .patterns.handlers import LoginHandler, RegisterHandler
from .patterns.commands import UpdateStatusCommand, UpdateRatingCommand, UpdateReviewCommand, CommandInvoker
from .patterns.search_handlers import TitleSearchHandler, AuthorSearchHandler, GenreSearchHandler, SortSearchHandler

# ==== PATTERN DECORATOR ====

def login_required_custom(function=None, redirect_field_name='next', login_url='login'):
    """
    Декоратор, який перевіряє, чи користувач автентифікований.
    Якщо ні, перенаправляє його на сторінку логіну.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated,
        login_url=login_url
    )
    
    if function:
        return actual_decorator(function)
    
    return actual_decorator


# login/register/logout
def logoutUser(request):
    logout(request)
    return redirect('login')

def loginUser(request):
    handler = LoginHandler()
    return handler.handle(request)

def registerUser(request):
    handler = RegisterHandler()
    return handler.handle(request)

def logoutUser(request):
    logout(request)
    return redirect('login')

class AddCommentView(CreateView):
    model = Comment
    template_name='add_comment.html'
    fields='__all__'


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
    queryset = Book.objects.all()

    # Chain of Responsibility
    title_handler = TitleSearchHandler()
    author_handler = AuthorSearchHandler()
    genre_handler = GenreSearchHandler()
    sort_handler = SortSearchHandler()
    title_handler.set_next_handler(author_handler).set_next_handler(genre_handler).set_next_handler(sort_handler)
    results = title_handler.handle(request, queryset)

    # Strategy + Factory
    sort_by = request.GET.get('sort', 'title')
    strategy = SortStrategyFactory.create_strategy(sort_by)
    results = strategy.sort(results)  # або BookSorter(strategy).sort(results)

    return render(request, 'search_results.html', {
        'results': results,
        'query': request.GET.get('q', ''),
        'search_by': request.GET.get('search_by', 'book_title'),
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

@login_required_custom(login_url='login')
def profile(request):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()

    invoker = CommandInvoker()

    if request.method == 'POST':
        book_id = request.POST.get('book')
        action = request.POST.get('action')
        status = request.POST.get('status')
        rating = request.POST.get('rating')
        review = request.POST.get('review')

        if book_id:
            try:
                book = Book.objects.get(id=book_id)
                user_book = UserBook.objects.get(session_key=session_key, book=book)

                if action == 'update_status' and status:
                    invoker.add_command(UpdateStatusCommand(user_book, status))
                elif action == 'update_rating' and rating:
                    invoker.add_command(UpdateRatingCommand(user_book, rating))
                elif action == 'update_review' and review:
                    invoker.add_command(UpdateReviewCommand(user_book, review))

                invoker.execute_commands()

                return redirect('profile')
            except (Book.DoesNotExist, UserBook.DoesNotExist):
                pass

    # Get books for the user
    user_books = UserBook.objects.filter(session_key=session_key)

    # You can filter by status if needed, for example:
    reading_books = user_books.filter(status='reading')
    read_books = user_books.filter(status='read')
    planning_books = user_books.filter(status='planning')

    return render(request, 'profile.html', {
        'form': UserBookForm(),
        'reading_books': reading_books,
        'read_books': read_books,
        'planning_books': planning_books,
    })


@login_required_custom(login_url='login')
def book_status(request, pk):
    book = get_object_or_404(Book, pk=pk)
    session_key = request.session.session_key
    if not session_key:
        request.session.create()

    user_book, _ = UserBook.objects.get_or_create(session_key=session_key, book=book)

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