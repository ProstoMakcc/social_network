from django.shortcuts import render, get_object_or_404
from .models import Chat
from django.contrib.auth.decorators import login_required


@login_required
def chat(request, pk):
    chat = get_object_or_404(Chat, pk=pk)
    
    messages = chat.messages.all()

    return render(request, 'messenger/chat.html', {'chat': chat, 'messages': messages})
