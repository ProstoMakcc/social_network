from django.urls import path
from . import views

urlpatterns = [
    path('chat/<int:pk>/', views.chat, name='chat'),
]