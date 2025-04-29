from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from .patterns.states import UnreadState, ReadingState, ReadState, PlanningState

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
    genre = models.CharField(max_length=250, default="none")
    ISBN = models.CharField(max_length=20)
    Publication_Country = models.CharField(max_length=100)
    Language = models.CharField(max_length=50)
    Publication_Year = models.IntegerField()


    def __str__(self):
        return self.book_title

# Клас UserBook 
class UserBook(models.Model):
    STATUS_CHOICES = [
        ('unread', 'Unread'),
        ('reading', 'Reading'),
        ('read', 'Read'),
        ('planning', 'Planning'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    # Видаляємо session_key, оскільки користувач буде використовувати свою сесію
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unread')
    rating = models.IntegerField(null=True, blank=True)  # Optional rating
    review = RichTextField(default="No review yet")

    def __str__(self):
        return f"{self.book.book_title} - {self.status}"

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    # Get the correct state object based on the status
    def get_state(self):
        state_map = {
            'unread': UnreadState(),
            'reading': ReadingState(),
            'read': ReadState(),
            'planning': PlanningState(),
        }
        return state_map.get(self.status, UnreadState())

    def update_status(self, status):
        current_state = self.get_state()
        current_state.update_status(self, status)

    def add_review(self, review):
        current_state = self.get_state()
        current_state.add_review(self, review)

    def add_rating(self, rating):
        current_state = self.get_state()
        current_state.add_rating(self, rating)

class BookRequest(models.Model):
    book_title = models.CharField(max_length=250)
    author = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)  # автоматично зберігає дату створення запиту

    def __str__(self):
        return f"Request for {self.book_title} by {self.author} on {self.created_at}"
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='profile_photos/', default='default.jpg')
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username
        
class Comment(models.Model):
    book = models.ForeignKey(Book, related_name="comments", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # ← дозволяємо null
    body = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.book.book_title} - {self.name}'
