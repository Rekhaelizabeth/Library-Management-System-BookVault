from django.urls import path
from . import views

urlpatterns = [
    path('view_subscription/', views.view_subscription, name='view_subscription'),
    path('digital-books/', views.search_digital_books, name='search_digital_books'),
    path('send_notification/', views.send_notification, name='send_notification'),
    
]
