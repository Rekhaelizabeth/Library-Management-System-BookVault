from django.urls import path
from . import views

urlpatterns = [
    path('add_tag/', views.add_tag, name='add_tag'),
    path('tag_list/', views.tag_list, name='tag_list'),
    path('tag_categorization/', views.tag_categorization, name='tag_categorization'),
    path('tag_categorization/<int:tag_id>/books/', views.books_by_tag, name='books_by_tag'),
    path('tagadmin_list/', views.tagadmin_list, name='tagadmin_list'),

    path('add_author/', views.add_author, name='add_author'),
    path('author_list/', views.author_list, name='author_list'),
    path('author-categorization/', views.author_categorization, name='author_categorization'),
    path('books-by-author/<int:author_id>/', views.books_by_author, name='books_by_author'),
    path('authoradmin_list/', views.authoradmin_list, name='authoradmin_list'),

    path('add_genre/', views.add_genre, name='add_genre'),
    path('genre_list/', views.genre_list, name='genre_list'),
    path('genres/', views.genre_categorization, name='genre_categorization'),
    path('genres/<int:genre_id>/', views.books_by_genre, name='books_by_genre'),
    path('genreadmin_list/', views.genreadmin_list, name='genreadmin_list'),

    path('add_book/', views.add_book, name='add_book'),
    path('book_list/', views.book_list, name='book_list'),
    path('viewbooks/', views.viewbooks, name='viewbooks'),
    path('book_transaction_list/', views.book_transaction_list, name='book_transaction_list'), 
    path('bookadmin_list/', views.bookadmin_list, name='bookadmin_list'),
    path('edit_book/<int:book_id>/', views.edit_book, name='edit_book'),
    path('books/<int:book_id>/remove/', views.remove_book, name='remove_book'),
    path('member_list/', views.member_list, name='member_list'),
    path('approve_member/<int:user_id>', views.approve_member, name='approve_member'),
    path('issue_book/', views.issue_book, name='issue_book'),
    path('approve_book_request/<int:transaction_id>/', views.approve_book_request, name='approve_book_request'), 
    path('approve_bookreturn_request/<int:transaction_id>/', views.approve_bookreturn_request, name='approve_bookreturn_request'), 
    path('approve_lostbook_request/<int:transaction_id>/', views.approve_lostbook_request, name='approve_lostbook_request'),  
    path('librairianreturn_book/', views.librairianreturn_book, name='return_book'),
    path('librairianlost_book/', views.librairianlost_book, name='librairianlost_book'),

    path('userviewprofile/', views.userviewprofile, name='userviewprofile'),

    path('cancel_reservation/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
]
