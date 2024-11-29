from django.urls import path
from . import views

urlpatterns = [
    path('view_subscription/', views.view_subscription, name='view_subscription'),
    path('digital-books/', views.search_digital_books, name='search_digital_books'),
    
]
