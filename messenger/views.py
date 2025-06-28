from django.shortcuts import render, get_object_or_404
from .models import Chat
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

def chat(request, pk):
    chat = get_object_or_404(Chat, id=pk)
    
    messages = chat.messages.all().order_by('timestamp')

    return JsonResponse({'messages': list(messages.values())})