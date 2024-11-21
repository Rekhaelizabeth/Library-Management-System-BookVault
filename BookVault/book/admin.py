from django.contrib import admin
from .models import Author, Genre, Book, Tag

# Register your models here
admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(Book)
admin.site.register(Tag)
