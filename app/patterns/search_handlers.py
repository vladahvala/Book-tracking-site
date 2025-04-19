# ==== PATTERN CHAIN OF RESPONSIBILITY ====

from django.db.models import Q
from ..models import Book

class SearchHandler:
    def __init__(self):
        self._next_handler = None
    
    def set_next_handler(self, handler):
        self._next_handler = handler
        return handler

    def handle(self, request, queryset):
        raise NotImplementedError


class TitleSearchHandler(SearchHandler):
    def handle(self, request, queryset):
        query = request.GET.get('q')
        if query and request.GET.get('search_by') == 'book_title':
            queryset = queryset.filter(Q(book_title__icontains=query))
        if self._next_handler:
            return self._next_handler.handle(request, queryset)
        return queryset


class AuthorSearchHandler(SearchHandler):
    def handle(self, request, queryset):
        query = request.GET.get('q')
        if query and request.GET.get('search_by') == 'author':
            queryset = queryset.filter(Q(author__icontains=query))
        if self._next_handler:
            return self._next_handler.handle(request, queryset)
        return queryset


class GenreSearchHandler(SearchHandler):
    def handle(self, request, queryset):
        query = request.GET.get('q')
        if query and request.GET.get('search_by') == 'genre':
            queryset = queryset.filter(Q(genre__icontains=query))
        if self._next_handler:
            return self._next_handler.handle(request, queryset)
        return queryset


class SortSearchHandler(SearchHandler):
    def handle(self, request, queryset):
        sort_by = request.GET.get('sort', 'book_title')
        if sort_by:
            queryset = queryset.order_by(sort_by)
        if self._next_handler:
            return self._next_handler.handle(request, queryset)
        return queryset