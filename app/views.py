from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import F
from .models import Book
from .utils import find_similar_books
from django.shortcuts import render, get_object_or_404
from .models import Book
from .utils import find_similar_books
import os
import fitz  # PyMuPDF
from django.db.models import Count
import plotly.graph_objs as go
from .models import Book, UserBook
from .forms import UserBookForm
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def search_books(request):
    query = request.GET.get('query', '')
    similar_books = []

    # Find similar books
    similar_books = find_similar_books(query, Book.objects.all())

    context = {
        'query': query,
        'similar_books': similar_books,
    }
    return render(request, 'home.html', context, )


def extract_pdf_details(pdf_path):
    document = fitz.open(pdf_path)
    num_pages = document.page_count
    file_size = os.path.getsize(pdf_path)  # in bytes
    file_size_mb = file_size / (1024 * 1024)  # in MB
    return num_pages, file_size_mb


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
# Перевірка на наявність session_key
    session_key = request.session.session_key
    if not session_key:
        request.session.create()  # Створюємо сесію, якщо вона відсутня

    # Тепер отримуємо або створюємо запис UserBook
    user_book, created = UserBook.objects.get_or_create(session_key=session_key, book=book)
    
    # Find similar books
    all_books = Book.objects.exclude(pk=pk)  # Exclude the current book from recommendations
    similar_books = find_similar_books(book.book_title, all_books)
     
    # Extract PDF details
    pdf_path = book.file.path
    num_pages, file_size_mb = extract_pdf_details(pdf_path)
    
    # Handle POST request for updating book status
    if request.method == 'POST':
        status = request.POST.get('status')

        # Use session for anonymous users, or 'user' for logged-in users
        session_key = request.session.session_key
        if not session_key:
            request.session.create()  # Create a session if not exists
        
        # Use session_key instead of user model for anonymous users
        user_book, created = UserBook.objects.get_or_create(session_key=session_key, book=book)

        if status == 'unread':
            # Remove book from the user's profile
            user_book.delete()
        else:
            # Update the status
            user_book.status = status
            user_book.save()

        

        return redirect('book_detail', pk=pk)

    context = {
        'book': book,
        'similar_books': similar_books,
        'num_pages': num_pages,
        'file_size_mb': file_size_mb,
        'user_book': user_book,  # Передаємо user_book у контекст
    }
    return render(request, 'book_detail.html', context)




def book_stats(request):
    # Query to get data
    data = Book.objects.values('Publication_Year', 'Category').annotate(count=Count('id'))

    # Extract unique categories and years for plotting
    categories = sorted(set(item['Category'] for item in data))
    years = sorted(set(item['Publication_Year'] for item in data))

    # Create empty dictionary to store counts by year for each category
    category_counts_by_year = {category: [0] * len(years) for category in categories}

    # Fill the dictionary with counts from the query
    for item in data:
        category_counts_by_year[item['Category']][years.index(item['Publication_Year'])] = item['count']

    # Plotly figure creation
    fig = go.Figure()

    for category in categories:
        fig.add_trace(go.Bar(
            x=years,
            y=category_counts_by_year[category],
            name=category
        ))

    fig.update_layout(
        barmode='stack',
        title='Stacked Vertical Bar Chart of Book Categories by Publication Year',
        xaxis_title='Publication Year',
        yaxis_title='Frequency',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='gray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='gray')
    # Convert the figure to HTML
    fig_html = fig.to_html(full_html=False)

    context = {
        'fig_html': fig_html
    }

    return render(request, 'trend.html', context)


def about(request):
    return render(request, 'about.html', )


def profile(request):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()

    if request.method == 'POST':
        book_id = request.POST.get('book')
        action = request.POST.get('action')
        status = request.POST.get('status')
        rating = request.POST.get('rating')

        # Обробка форми оновлення статусу та рейтингу
        if book_id:
            try:
                book = Book.objects.get(id=book_id)
                user_book = UserBook.objects.get(session_key=session_key, book=book)

                # Оновлення статусу
                if action == 'update_status' and status:
                    if status == 'unread':
                        user_book.delete()
                        return redirect('profile')
                    else:
                        user_book.status = status
                        user_book.save()

                # Оновлення рейтингу
                elif action == 'update_rating' and rating:
                    user_book.rating = int(rating)
                    user_book.save()

                # Оновлення відгуку
                elif action == 'update_review' and book_id:
                    review = request.POST.get('review')
                    user_book.review = review
                    user_book.save()

                return redirect('profile')

            except (Book.DoesNotExist, UserBook.DoesNotExist):
                pass

    # Getting page parameters from GET request
    reading_page = request.GET.get('reading_page', 1)
    read_page = request.GET.get('read_page', 1)
    planning_page = request.GET.get('planning_page', 1)

    # Fetching books and creating paginators for each category
    reading_books = UserBook.objects.filter(status='reading', session_key=session_key)
    read_books = UserBook.objects.filter(status='read', session_key=session_key)
    planning_books = UserBook.objects.filter(status='planning', session_key=session_key)

    reading_paginator = Paginator(reading_books, 6)
    read_paginator = Paginator(read_books, 6)
    planning_paginator = Paginator(planning_books, 6)

    # Getting the necessary pages
    user_books_reading = reading_paginator.get_page(reading_page)
    user_books_read = read_paginator.get_page(read_page)
    user_books_planning = planning_paginator.get_page(planning_page)

    form = UserBookForm()

    return render(request, 'profile.html', {
        'user_books_reading': user_books_reading,
        'user_books_read': user_books_read,
        'user_books_planning': user_books_planning,
        'form': form,
    })


def book_status(request, pk):
    book = get_object_or_404(Book, pk=pk)

    # шукаємо, чи вже є запис UserBook
    session_key = request.session.session_key
    if not session_key:
        request.session.create()  # Створюємо сесію, якщо вона відсутня

    # Тепер отримуємо або створюємо запис UserBook
    user_book, created = UserBook.objects.get_or_create(session_key=session_key, book=book)

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
