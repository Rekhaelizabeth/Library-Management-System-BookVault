from django.urls import path
from . import views

urlpatterns = [
    path('book_list/', views.book_list, name='book_list'),
    path('add_tag/', views.add_tag, name='add_tag'),
    path('add_genre/', views.add_genre, name='add_genre'),
    path('add_book/', views.add_book, name='add_book'),
    path('add_author/', views.add_author, name='add_author'),
    path('inventory/', views.inventory, name='inventory'),
]
