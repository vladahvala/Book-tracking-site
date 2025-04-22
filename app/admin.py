from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Book
from .resources import BookResource
from .models import BookRequest

class BookAdmin(ImportExportModelAdmin):
    resource_class = BookResource
    list_display = ('id', 'book_title', 'book_name', 'author', 'created_date','Category','ISBN',)
    #list_filter = ("book_title","book_name",)
    search_fields = ("book_title","book_name","year",'Category')
    list_per_page = 10
    list_max_show_all = 50
    list_editable=("author",)
admin.site.register(Book, BookAdmin)

class BookRequestAdmin(admin.ModelAdmin):
    list_display = ('book_title', 'author', 'created_at')  # Використовуємо поле created_at
    list_filter = ('created_at',)  # Можна фільтрувати по даті створення запиту
    search_fields = ('book_title', 'author')  # Пошук по назві та автору книги

admin.site.register(BookRequest, BookRequestAdmin)