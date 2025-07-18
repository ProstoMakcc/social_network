from django.db import models
from auth_system.models import CustomUser
from datetime import datetime


class Chat(models.Model):
    name = models.CharField(max_length=20)
    participants = models.ManyToManyField(CustomUser)
    last_message = models.DateTimeField(default=datetime.today())

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True, related_name="messages")
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    