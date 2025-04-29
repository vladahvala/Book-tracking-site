from django.shortcuts import render, get_object_or_404, redirect
from .utils.utils import find_similar_books
from .models import Book, UserBook, Comment, UserProfile
from .forms import UserBookForm, UserProfileForm

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
from django.http import HttpResponse
from .models import BookRequest

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .patterns.factories import SortStrategyFactory
from .patterns.handlers import LoginHandler, RegisterHandler
from .patterns.commands import UpdateStatusCommand, UpdateRatingCommand, UpdateReviewCommand, CommandInvoker
from .patterns.search_handlers import TitleSearchHandler, AuthorSearchHandler, GenreSearchHandler, SortSearchHandler
from .patterns.states import UnreadState, ReadingState, ReadState
from .patterns.services import BookDetailBuilder
# from .patterns.abstract_factories import (
#     BusinessLiteratureFactory, DetectivesAndThrillersFactory, NonfictionLiteratureFactory,
#     HomeAndFamilyFactory, ArtAndDesignFactory, ComputersAndInternetFactory, 
#     ChildrensLiteratureFactory, RomanceNovelsFactory, ScienceAndEducationFactory,
#     PoetryFactory, AdventureFactory, ProseFactory, SciFiAndFantasyFactory, HumorFactory
# )
from .patterns.abstract_factories import DynamicCategoryFactory

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



# ==== GENERAL VIEWS ====

# book genres 
# (books sorted in categories)
def genres(request):
    # Початкові категорії та підкатегорії
#     categories_config = {
#         "Business Literature": ["Business Literature", "Career & HR", "Marketing & PR", "Finance", "Economics"],
#         "Detectives and Thrillers": ["Action", "Detectives", "Humorous & Women's Detectives", "Historical Detective", 
# "Classic Detective", "Crime Detective", "Hard-Boiled Detective", "Political Detective", 
# "Police Detective", "Maniac Stories", "Soviet Detective", "Thriller", "Espionage Detective"],
#         "Nonfiction Literature": ["Biographies & Memoirs", "Military Documentary & Analysis", "Military Science", 
# "Geography & Travel Notes", "General Nonfiction", "Journalism & Publicism"],
#         "Home and Family": ["Cars & Traffic Rules", "Martial Arts & Sports", "Pets", "Home Economics", "Health", "Cooking", "Entertainment"],
#         "Art and Design": ["Painting, Albums, Illustrated Catalogs", "Art & Design", "Art Criticism", "Cinema & Film", 
# "Music", "Theatre", "Sculpture & Architecture"],
#         "Computers and Internet": ["Foreign Computer Literature", "Computer Hardware & Digital Signal Processing", 
# "Operating Systems, Networks & Internet", "Programming, Software & Databases", 
# "Computer Tutorials & Guides"],
#         "Children's Literature": ["General Children's Literature", "Educational Literature for Children", 
# "Thrilling Literature for Children", "Games & Exercises for Children", "World Folk Tales"],
#         "Romance Novels": ["Historical Romance", "Short Romance Stories", "Romantic Fantasy", "Romantic Thrillers", "Contemporary Romance"],
#         "Science and Education": ["Alternative Medicine", "Alternative Sciences & Theories", "Biology, Biophysics & Biochemistry", 
# "Military History", "Law & Government"],
#         "Poetry": ["Classical foreign poetry", "Song lyrics poetry", "Modern foreign poetry"],
#         "Adventure": ["Adventure novel", "Adventures", "Modern world adventures", "Nature and animals", "Maritime adventures"],
#         "Prose": ["Gothic novel", "Classical prose of the 19th century", "War prose", "Phantasmagoria, absurdist prose", "Epistolary prose"],
#         "Sci-Fi and Fantasy": ["Heroic fantasy", "Cyberpunk", "Mythological fantasy", "Dystopia", "Post-apocalypse", "Slavic fantasy", 
# "Horror", "Steampunk", "Fantasy", "Epic science fiction", "Fairytale", "Modern fairy tale"],
#         "Humor": ["Jokes", "Satire", "Humor"]
#     }

    # Створення однієї універсальної фабрики
    factory = DynamicCategoryFactory()

    categories = factory.categories  # Отримуємо категорії з фабрики
    books_by_subcategory = []

    for main_category, subcategories in categories.items():
        for subcategory in subcategories:
            # Отримуємо книжки за жанром (підкатегорією)
            books = list(Book.objects.filter(Category=main_category, genre=subcategory).values('id', 'book_title', 'author'))
            books_by_subcategory.append((subcategory, books))

    return render(request, 'genres.html', {
        'categories': categories,
        'books_by_subcategory': books_by_subcategory,
    })



# search for a certain book by title/author/genre
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


# book recommendations 
# (seraching for book recs using Word2Vec model)
def search_books(request):
    query = request.GET.get('query', '')
    similar_books = find_similar_books(query, Book.objects.all())

    return render(request, 'recommendations.html', {
        'query': query,
        'similar_books': similar_books,
    })


# book request 
# (user can send a request too admin about what book should be added)
def submit_book_request(request):
    if request.method == 'POST':
        book_title = request.POST.get('book_title')
        author = request.POST.get('author')
        BookRequest.objects.create(book_title=book_title, author=author)

        return JsonResponse({'message': 'Thank you for your request! We will add the book soon.'}, status=200)
    
    return JsonResponse({'message': 'Invalid request'}, status=400)


# book stats
# (showing most popular book genres in certain years using bar chart)
def book_stats(request):
    data = Book.objects.exclude(genre__iexact='none').values('Publication_Year', 'genre').annotate(count=Count('id'))

    genres = sorted(set(item['genre'] for item in data))
    years = sorted(set(item['Publication_Year'] for item in data))

    genre_counts_by_year = {genre: [0] * len(years) for genre in genres}
    for item in data:
        genre_counts_by_year[item['genre']][years.index(item['Publication_Year'])] = item['count']

    fig = go.Figure()
    for genre in genres:
        counts = genre_counts_by_year[genre]
        fig.add_trace(go.Bar(x=years, y=counts, name=genre))

    fig.update_layout(
        barmode='stack',
        title='Stacked Vertical Bar Chart of Book Genres by Publication Year',
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


# book сcomments
# (adding comments to books)
class AddCommentView(CreateView):
    model = Comment
    template_name = 'add_comment.html'
    fields = ['body']  # Лише body, name заповнюється автоматично

    def form_valid(self, form):
        book = get_object_or_404(Book, pk=self.kwargs['pk'])
        form.instance.book = book
        form.instance.user = self.request.user
        form.instance.name = self.request.user.username  # 🧩 автоматично з юзера
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = get_object_or_404(Book, pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        return redirect('book_detail', pk=self.kwargs['pk']).url
    
   
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Перевірка чи користувач є адміністратором або автором коментаря
    if request.user.is_superuser or comment.user == request.user:
        comment.delete()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'You are not authorized to delete this comment.'})


# ==== AUTH VIEWS ====

# book properties for each book
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    user = request.user if request.user.is_authenticated else None  

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
    builder = BookDetailBuilder(book, user)
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

    # Логіка зміни статусу (тільки для авторизованих користувачів)
    if request.method == 'POST' and user:  # Тільки для авторизованих користувачів
        status = request.POST.get('status')
        user_book, _ = UserBook.objects.get_or_create(user=user, book=book)

        if status == 'unread':
            user_book.delete()  
        else:
            user_book.status = status
            user_book.save()

        return redirect('book_detail', pk=pk)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"status": "confirmed", "file_url": book.file.url})

    return render(request, 'book_detail.html', context)



# profile book page 
# (books sorted in tabs reading/read/planning)
@login_required_custom(login_url='login')
def profile(request):
    user = request.user
    invoker = CommandInvoker()

    # Отримуємо або створюємо профіль
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    # --- Обробка змін книжки --- 
    if request.method == 'POST' and request.POST.get('action'):
        book_id = request.POST.get('book')
        action = request.POST.get('action')
        status = request.POST.get('status')
        rating = request.POST.get('rating')
        review = request.POST.get('review')

        if book_id:
            try:
                book = Book.objects.get(id=book_id)
                user_book = UserBook.objects.get(user=user, book=book)

                if action == 'update_status' and status:
                    invoker.add_command(UpdateStatusCommand(user_book, status))
                elif action == 'update_rating' and rating:
                    invoker.add_command(UpdateRatingCommand(user_book, rating))
                elif action == 'update_review' and review:
                    invoker.add_command(UpdateReviewCommand(user_book, review))

                invoker.execute_commands()
                messages.success(request, "Інформацію про книжку оновлено.")
                return redirect('profile')
            except (Book.DoesNotExist, UserBook.DoesNotExist):
                messages.error(request, "Книжку не знайдено або її немає у вашому списку.")

    # --- Обробка зміни біо ---
    if request.method == 'POST' and 'update_bio' in request.POST:
        bio = request.POST.get('bio')
        if bio:
            user_profile.bio = bio
            user_profile.save()
            messages.success(request, "Біо оновлено.")
            return redirect('profile')

    # --- Обробка зміни фото ---
   # --- Обробка зміни фото через AJAX ---
    if request.method == 'POST' and 'update_photo' in request.POST:
        if 'photo' in request.FILES:
            photo = request.FILES['photo']
            user_profile.photo = photo
            user_profile.save()
            return JsonResponse({
                'success': True,
                'new_photo_url': user_profile.photo.url
            })
        else:
            return JsonResponse({'success': False, 'error': 'Фото не надано.'})

    # --- Обробка форми профілю --- 
    if request.method == 'POST' and 'update_profile' in request.POST:
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Профіль оновлено.")
            return redirect('profile')
    else:
        profile_form = UserProfileForm(instance=user_profile)

    # --- Дані про книжки --- 
    user_books = UserBook.objects.filter(user=user)
    reading_books = user_books.filter(status='reading')
    read_books = user_books.filter(status='read')
    planning_books = user_books.filter(status='planning')

    # --- Пагінація --- 
    reading_page = request.GET.get('reading_page', 1)
    read_page = request.GET.get('read_page', 1)
    planning_page = request.GET.get('planning_page', 1)

    reading_paginator = Paginator(reading_books, 6)
    read_paginator = Paginator(read_books, 6)
    planning_paginator = Paginator(planning_books, 6)

    reading_books_page = reading_paginator.get_page(reading_page)
    read_books_page = read_paginator.get_page(read_page)
    planning_books_page = planning_paginator.get_page(planning_page)

    return render(request, 'profile.html', {
        'form': UserBookForm(),
        'profile_form': profile_form,
        'user_profile': user_profile,
        'reading_books_page': reading_books_page,
        'read_books_page': read_books_page,
        'planning_books_page': planning_books_page,
    })

# book status
# (reading for books in process/read for read books/planning for books the user 
#  is planning to read/unread for all other books)
@login_required_custom(login_url='login')
def book_status(request, pk):
    book = get_object_or_404(Book, pk=pk)
    user = request.user  

    user_book, _ = UserBook.objects.get_or_create(user=user, book=book)

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
