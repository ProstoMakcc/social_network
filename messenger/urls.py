from django.urls import path
from . import views

urlpatterns = [
    path('lobby/', views.lobby, name='lobby'),
    path('create-message/<int:pk>', views.create_message, name='create-message'),
    path('stream-chat-messages/<int:pk>', views.stream_chat_messages, name='stream-chat-messages'),
    path('chat/users/', views.users_suggestions, name='user-suggestions'),
]