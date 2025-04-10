from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField

class Book(models.Model):
    id = models.AutoField(primary_key=True)
    book_title = models.CharField(max_length=250)
    book_name = models.CharField(max_length=250)
    book_annotation = RichTextField(default="No annotation yet")
    author = models.CharField(max_length=250)
    created_date = models.DateTimeField(default=timezone.now)
    file = models.FileField(upload_to='books/pdfs', default='books/pdfs/default.pdf')
    image = models.ImageField(upload_to='books/images', default='/media/books/images/default.png')
    search_count = models.IntegerField(default=0)
    Category = models.CharField(max_length=100)
    ISBN = models.CharField(max_length=20)
    Publication_Country = models.CharField(max_length=100)
    Language = models.CharField(max_length=50)
    Publication_Year = models.IntegerField()

    def __str__(self):
        return self.book_title

class UserBook(models.Model):
    STATUS_CHOICES = [
        ('unread', 'Unread'),
        ('reading', 'Reading'),
        ('read', 'Read'),
        ('planning', 'Planning'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)  # For anonymous users
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unread')

    def __str__(self):
        return f"{self.book.title} - {self.status}"

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)