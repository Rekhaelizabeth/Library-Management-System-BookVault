from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path("register_librarian/", views.register_librarian, name="register_librarian"),
    path("register_membercategory/", views.register_membercategory, name="register_membercategory"),
]
