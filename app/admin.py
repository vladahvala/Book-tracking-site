from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Book
from .resources import BookResource

class BookAdmin(ImportExportModelAdmin):
    resource_class = BookResource
    list_display = ('id', 'book_title', 'book_name', 'author', 'created_date','Category','ISBN',)
    #list_filter = ("book_title","book_name",)
    search_fields = ("book_title","book_name","year",'Category')
    list_per_page = 10
    list_max_show_all = 50
    list_editable=("author",)
admin.site.register(Book, BookAdmin)
