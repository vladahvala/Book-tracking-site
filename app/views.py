from django.shortcuts import render, get_object_or_404, redirect
from .utils.utils import find_similar_books
from .models import Book, UserBook, Comment
from .forms import UserBookForm

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
from .patterns.states import UnreadState, ReadingState, ReadState
from .patterns.services import BookDetailBuilder
from .patterns.abstract_factories import (
    BusinessLiteratureFactory, DetectivesAndThrillersFactory, NonfictionLiteratureFactory,
    HomeAndFamilyFactory, ArtAndDesignFactory, ComputersAndInternetFactory, 
    ChildrensLiteratureFactory, RomanceNovelsFactory, ScienceAndEducationFactory,
    PoetryFactory, AdventureFactory, ProseFactory, SciFiAndFantasyFactory, HumorFactory
)

from app.utils.pdf_utils import PDFProxy

# ==== PATTERN DECORATOR ==== 
# Structural 

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
    # Створення фабрик для категорій
    factories = [
        BusinessLiteratureFactory(),
        DetectivesAndThrillersFactory(),
        NonfictionLiteratureFactory(),
        HomeAndFamilyFactory(),
        ArtAndDesignFactory(),
        ComputersAndInternetFactory(),
        ChildrensLiteratureFactory(),
        RomanceNovelsFactory(),
        ScienceAndEducationFactory(),
        PoetryFactory(),
        AdventureFactory(),
        ProseFactory(),
        SciFiAndFantasyFactory(),
        HumorFactory()
    ]
    
    categories = {}
    books_by_subcategory = []

    # Використовуємо фабрики для отримання категорій та книжок
    for factory in factories:
        category_names = factory.create_categories()
        categories.update({category_names[0]: category_names})  # додаємо перше значення як ключ
        
        # Отримуємо книжки для кожної підкатегорії
        books = list(factory.create_books_by_subcategory())
        for category in category_names:
            books_by_subcategory.append((category, books))

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

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)

    session_key = request.session.session_key
    if not session_key:
        request.session.create()

    confirm = request.GET.get("confirm_download", "false") == "true"

    # Перевірка розміру файлу через проксі
    proxy = PDFProxy(book.file.path)
    try:
        file_too_large = proxy.is_too_large()
        file_size = f"{proxy.file_size:.2f} MB" if proxy.file_size else None
    except Exception:
        file_too_large = False
        file_size = None

    # Побудова деталей книги
    builder = BookDetailBuilder(book, session_key)
    builder.set_user_book() \
           .set_similar_books(Book.objects.exclude(pk=pk))

    # Завантажувати PDF-деталі тільки якщо не великий файл або є підтвердження
    if not file_too_large or confirm:
        builder.set_pdf_details()
    else:
        builder.num_pages = None
        builder.file_size = file_size

    context = builder.build()
    context.update({
        "book": book,
        "is_large_file": file_too_large,
        "file_size": file_size,
        "confirm_download": confirm,
        "num_pages": builder.num_pages,
        "file_size_mb": builder.file_size,
    })

    if request.method == 'POST':
        status = request.POST.get('status')
        user_book, _ = UserBook.objects.get_or_create(session_key=session_key, book=book)

        if status == 'unread':
            user_book.delete()
        else:
            user_book.status = status
            user_book.save()

        return redirect('book_detail', pk=pk)

    # Якщо користувач натискає кнопку для підтвердження завантаження
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"status": "confirmed", "file_url": book.file.url})

    return render(request, 'book_detail.html', context)



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

    user_books = UserBook.objects.filter(session_key=session_key)
    reading_books = user_books.filter(status='reading')
    read_books = user_books.filter(status='read')
    planning_books = user_books.filter(status='planning')

    # Pagination for each group of books
    reading_page = request.GET.get('reading_page', 1)
    read_page = request.GET.get('read_page', 1)
    planning_page = request.GET.get('planning_page', 1)

    # Create Paginator objects for each group
    reading_paginator = Paginator(reading_books, 6)  # 6 books per page
    read_paginator = Paginator(read_books, 6)
    planning_paginator = Paginator(planning_books, 6)

    # Get the current page for each category
    reading_books_page = reading_paginator.get_page(reading_page)
    read_books_page = read_paginator.get_page(read_page)
    planning_books_page = planning_paginator.get_page(planning_page)

    return render(request, 'profile.html', {
        'form': UserBookForm(),
        'reading_books_page': reading_books_page,
        'read_books_page': read_books_page,
        'planning_books_page': planning_books_page,
    })


@login_required_custom(login_url='login')
def book_status(request, pk):
    book = get_object_or_404(Book, pk=pk)
    session_key = request.session.session_key
    if not session_key:
        request.session.create()

    user_book, _ = UserBook.objects.get_or_create(session_key=session_key, book=book)

    # Вибір стану на основі поточного статусу
    if user_book.status == 'unread':
        state = UnreadState()
    elif user_book.status == 'reading':
        state = ReadingState()
    elif user_book.status == 'read':
        state = ReadState()

    if request.method == 'POST':
        form = UserBookForm(request.POST, instance=user_book)
        rating = request.POST.get('rating')
        review = request.POST.get('review')

        if form.is_valid():
            if form.cleaned_data['status'] != user_book.status:
                # Оновлення статусу через відповідний стан
                state.update_status(user_book, form.cleaned_data['status'])
            
            if review:
                # Додавання відгуку через стан
                state.add_review(user_book, review)
            
            if rating:
                # Додавання рейтингу через стан
                state.add_rating(user_book, rating)
            
            return redirect('profile')
    else:
        form = UserBookForm(instance=user_book)

    return render(request, 'app/book_detail.html', {
        'book': book,
        'form': form,
    })