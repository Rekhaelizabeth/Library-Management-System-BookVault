from django.urls import path
from . import views

urlpatterns = [
    path('book_list/', views.book_list, name='book_list'),
    path('add_tag/', views.add_tag, name='add_tag'),
    path('add_genre/', views.add_genre, name='add_genre'),
    path('add_book/', views.add_book, name='add_book'),
    path('add_author/', views.add_author, name='add_author'),
    path('inventory/', views.inventory, name='inventory'),
    path('viewbooks/', views.viewbooks, name='viewbooks'),
    path('book_transaction_list/', views.book_transaction_list, name='book_transaction_list'),
    path('tag_list/', views.tag_list, name='tag_list'),
    path('genre_list/', views.genre_list, name='genre_list'),
    path('author_list/', views.author_list, name='author_list'),
    path('edit_book/<int:book_id>/', views.edit_book, name='edit_book'),
    path('books/<int:book_id>/remove/', views.remove_book, name='remove_book'),
    path('member_list/', views.member_list, name='member_list'),
    path('approve_member/<int:user_id>', views.approve_member, name='approve_member'),
]
