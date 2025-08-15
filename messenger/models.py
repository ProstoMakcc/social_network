from django.db import models
from auth_system.models import CustomUser


class Chat(models.Model):
    name = models.CharField(max_length=20)
    chat_image = models.ImageField(upload_to='chat_image', default='chat_image_default.png')
    participants = models.ManyToManyField(CustomUser)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    last_message = models.ForeignKey('Message', on_delete=models.SET_NULL, null=True, blank=True, related_name='last_in_chats')

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True, related_name="messages")
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    