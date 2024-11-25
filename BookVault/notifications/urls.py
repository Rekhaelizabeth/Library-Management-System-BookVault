from django.urls import path
from . import views

urlpatterns = [
    path('list_subscriptions/', views.list_subscriptions, name='list_subscriptions'),
    path('subscriptions/<int:subscription_id>/subscribe/', views.subscribe_to_plan, name='subscribe_to_plan'),
    path('subscriptions/success/', views.subscription_success, name='subscription_success'),
    path("subscriptions/<int:subscription_id>/subscribe/", views.subscribe_to_plan, name="subscribe_to_plan"),

   
]
