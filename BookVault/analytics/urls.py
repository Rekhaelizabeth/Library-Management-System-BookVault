from django.urls import path
from . import views

urlpatterns = [
    path('view_subscription/', views.view_subscription, name='view_subscription'),
    path('digital-books/', views.search_digital_books, name='search_digital_books'),
    path('send_notification/', views.send_notification, name='send_notification'),
    path('adminbook_analytics/', views.adminbook_analytics, name='adminbook_analytics'),
    path('books_by_genre_analytics/', views.books_by_genre_analytics, name='books_by_genre_analytics'),
    path('books_by_author_analytics/', views.books_by_author_analytics, name='books_by_author_analytics'),
    path('membernotifications/', views.membernotifications, name='membernotifications'),
    path('inventory/', views.inventory, name='inventory'),
    path('update_copies_post/<int:book_id>/', views.update_copies_post, name='update_copies_post'),  
    path('penalty/', views.penalty, name='penalty'),
    path('pay_penalty/', views.pay_penalty, name='pay_penalty'), 
]
