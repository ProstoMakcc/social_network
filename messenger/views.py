import asyncio
from typing import AsyncGenerator
from django.shortcuts import render, redirect
from django.http import HttpRequest, StreamingHttpResponse, HttpResponse, JsonResponse
from . import models
from auth_system import models as authModels
import json
from asgiref.sync import sync_to_async
from django.contrib.auth.decorators import login_required

@login_required
def lobby(request):
    if request.method == 'POST':
        user_id = request.POST["user-suggestions-dropdown"]
        user = authModels.CustomUser.objects.get(id=user_id)
        chat = models.Chat.objects.filter(participants=request.user).filter(participants=user).distinct().first()
        if not chat:
            chat = models.Chat.objects.create(name=f"{user.username}")
            chat.participants.add(user)
            chat.participants.add(request.user)
            chat.save()

        return redirect('lobby')
    else:
        user = request.user
        chats = models.Chat.objects.filter(participants=user).order_by('last_message') # TODO Provide last message functionality
        
        return render(request, 'messenger/lobby.html', {'chats': chats})

def create_message(request, pk):
    chat = models.Chat.objects.get(pk=pk)
    content = request.POST.get("content")
    user = request.user

    if not user:    
        return HttpResponse(status=403)

    if content:
        models.Message.objects.create(author=user, content=content, chat=chat)
        return HttpResponse(status=201)
    else:
        return HttpResponse(status=200)

async def stream_chat_messages(request, pk):
    chat = await sync_to_async(models.Chat.objects.get)(pk=pk)

    async def event_stream():
        async for message in get_existing_messages():
            yield message

        last_id = await get_last_message_id()

        while True:
            new_messages = models.Message.objects.filter(chat=chat).filter(id__gt=last_id).order_by('created_at').values(
                'id', 'author__username', 'content'
            )
            async for message in new_messages:
                yield f"data: {json.dumps(message)}\n\n"
                last_id = message['id']
            await asyncio.sleep(0.1)

    async def get_existing_messages():
        messages = models.Message.objects.filter(chat=chat).order_by('created_at').values(
            'id', 'author__username', 'content'
        )
        async for message in messages:
            yield f"data: {json.dumps(message)}\n\n"

    async def get_last_message_id() -> int:
        last_message = await models.Message.objects.filter(chat=chat).alast()

        return last_message.pk if last_message else 0

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

def users_suggestions(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")

        users = authModels.CustomUser.objects.filter(username__startswith=username).exclude(pk=request.user.pk)
        user_suggestions = []

        for user in users:
            user_suggestions.append({
                "id": user.pk,
                "username": user.username,
            })

        return JsonResponse({'user_suggestions': user_suggestions})
    
