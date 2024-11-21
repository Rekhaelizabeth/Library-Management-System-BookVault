from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path("register_librarian/", views.register_librarian, name="register_librarian"),
    path("register_membercategory/", views.register_membercategory, name="register_membercategory"),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('librarian_dashboard/', views.librarian_dashboard, name='librarian_dashboard'),
    path('member_dashboard/', views.member_dashboard, name='member_dashboard'),
]
