from django.shortcuts import render, redirect
from . import models
from auth_system import models as authModels
from django.contrib.auth.decorators import login_required

@login_required
def chat(request):
    if request.method == 'POST':
        user_id = request.POST["user-suggestions-dropdown"]
        user = authModels.CustomUser.objects.get(id=user_id)
        chat = models.Chat.objects.filter(participants=request.user).filter(participants=user).distinct().first()
        if not chat:
            chat = models.Chat.objects.create(name=f"{user.username}")
            chat.participants.add(user)
            chat.participants.add(request.user)
            chat.save()

        return redirect('chat')
    else:
        chats_qr = models.Chat.objects.filter(participants=request.user).order_by("-last_message__created_at")
        chats = []

        for chat in chats_qr:
            chats.append({
                'pk': chat.pk,
                'name': chat.name if len(chat.participants.all()) > 2 else chat.participants.exclude(pk=request.user.pk).distinct().first().username,
                'last_message': chat.last_message
            })
        
        return render(request, 'messenger/chat.html', {'chats': chats})
