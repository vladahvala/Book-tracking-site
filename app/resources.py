from import_export import resources
from .models import Book

class BookResource(resources.ModelResource):
    class Meta:
        model = Book
        fields = ('id', 'book_title', 'book_name', 'author', 'created_date','Category','ISBN','Publication_Country','Language','Publication_Year')  # Specify the fields to include
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = True
