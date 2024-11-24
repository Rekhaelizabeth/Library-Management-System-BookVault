from django.urls import path
from . import views

urlpatterns = [
    path('list_subscriptions/', views.list_subscriptions, name='list_subscriptions'),

]
