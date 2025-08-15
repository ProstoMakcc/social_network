from django.shortcuts import render, redirect
from . import models
from auth_system import models as authModels
from django.contrib.auth.decorators import login_required

@login_required
def chat(request):
    chats_qr = models.Chat.objects.filter(participants=request.user).order_by("-last_message__created_at")
    chats = []

    for chat in chats_qr:
        if len(chat.last_message.content) > 10:
            chat.last_message.content = chat.last_message.content[0:10] + "..."

        chats.append({
            'pk': chat.pk,
            'chat_image': chat.chat_image,
            'name': chat.name if len(chat.participants.all()) > 2 else chat.participants.exclude(pk=request.user.pk).distinct().first().username,
            'last_message': chat.last_message
        })
        
    return render(request, 'messenger/chat.html', {'chats': chats})
