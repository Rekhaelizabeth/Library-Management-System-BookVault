from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('baseindex/', views.baseindex, name='baseindex'),
    path('login/', views.user_login, name='login'),
    path("register_librarian/", views.register_librarian, name="register_librarian"),
    path("register_membercategory/", views.register_membercategory, name="register_membercategory"),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('librarian_dashboard/', views.librarian_dashboard, name='librarian_dashboard'),
    path('member_dashboard/', views.member_dashboard, name='member_dashboard'),
    path('add_subscription/', views.add_subscription, name='add_subscription'),
    path('admindashboard/', views.admindashboard, name='admindashboard'),
    path('logout/', views.custom_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('generate_qr_code/', views.generate_qr_code, name='generate_qr_code'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('reserve/<int:book_id>/', views.reserve_book, name='reserve_book'),
    path('book/<int:book_id>/', views.book_description, name='book_description'),

    
]
