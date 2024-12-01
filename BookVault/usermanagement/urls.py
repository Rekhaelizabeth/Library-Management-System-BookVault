from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

    path('error403/', views.error403, name='error403'),
    path('baseindex/', views.baseindex, name='baseindex'),
    path('librarianbaseindex/', views.librarianbaseindex, name='librarianbaseindex'),
    path('baseindexmember/', views.baseindexmember, name='baseindexmember'),
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
    path('memberview/', views.memberview, name='memberview'),
    path('access-denied/', views.access_denied, name='access_denied'),
    path('upload_membership_card/', views.upload_membership_card, name='upload_membership_card'),
    path('suggestions/', views.suggestion_view, name='suggestions'),
    path('return-book/<int:transaction_id>/', views.return_book, name='return_book'),
    path('lost_book/<int:transaction_id>/', views.lost_book, name='lost_book'),



    
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    
]
