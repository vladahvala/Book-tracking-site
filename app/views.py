from django.shortcuts import render, get_object_or_404
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
    
    # Find similar books
    all_books = Book.objects.exclude(pk=pk)  # Exclude the current book from recommendations
    similar_books = find_similar_books(book.book_title, all_books)
     
    # Extract PDF details
    pdf_path = book.file.path
    num_pages, file_size_mb = extract_pdf_details(pdf_path)

    context = {
        'book': book,
        'similar_books': similar_books,
        'num_pages': num_pages,
        'file_size_mb': file_size_mb,
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

















 




   
