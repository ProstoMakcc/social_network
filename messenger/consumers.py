from channels.generic.websocket import AsyncWebsocketConsumer
import json
from auth_system.models import OnlineUser, CustomUser
from channels.db import database_sync_to_async
from .models import Chat, Message

class MessengerConsumers(AsyncWebsocketConsumer):
    def get_chats(self):
        chats = Chat.objects.filter(participants=self.user).order_by('-last_message__created_at')

        return chats

    def change_user_online_status(self, online_status):
        if online_status == True:
            try:
                online_user = OnlineUser.objects.get(user=self.user)
                online_user.delete()
            except OnlineUser.DoesNotExist:
                pass
            
            OnlineUser.objects.create(user=self.user, channel_name=self.channel_name)
        else:
            user = OnlineUser.objects.filter(user=self.user)
            user.delete()
    
    def create_message(self, content, chatpk):
        message = Message.objects.create(author=self.user, content=content, chat_id=chatpk)

        chat = Chat.objects.get(pk=chatpk)
        chat.last_message = message
        chat.save()

        return message
    
    def create_chat(self, participant_pk):
        participant = CustomUser.objects.get(pk=participant_pk)
        chat = Chat.objects.create(name=self.user.username)
        chat.participants.add(participant, self.user)
        chat.save()

        return chat
    
    async def save_n_send_message(self, chatpk, content):
        message_obj = await database_sync_to_async(self.create_message)(content, chatpk)
        message = {
            'type': 'chat_message',
            'action': 'new_message',
            'message': {
                "new_message": {
                    "pk": message_obj.pk,
                    'author_avatar': await database_sync_to_async(lambda: message_obj.author.avatar.url)(),
                    "author": await database_sync_to_async(lambda: message_obj.author.username)(),
                    "content": message_obj.content,
                    "chat": await database_sync_to_async(lambda: message_obj.chat.pk)(),
                    "created_at": str(message_obj.created_at)
                }
            }
        }

        await self.channel_layer.group_send(f'chat_{chatpk}', message)

    async def save_n_send_chat(self, participant_pk):
        chat = await database_sync_to_async(self.create_chat)(participant_pk)
        participant_channel_name = await database_sync_to_async(lambda: OnlineUser.objects.get(user_id=participant_pk).channel_name)()

        group_name = f'chat_{chat.pk}'

        self.chats.append(group_name)
        await self.channel_layer.group_add(group_name, self.channel_name)
        await self.channel_layer.group_add(group_name, participant_channel_name)

        message = {
            'type': 'chat_message',
            'action': 'new_chat',
            'message': {
                'chat': {
                    'pk': chat.pk,
                    'name': await database_sync_to_async(lambda: chat.name if len(chat.participants.all()) > 2 else chat.participants.exclude(pk=self.user.pk).distinct().first().username)(),
                    'last_message': (await database_sync_to_async(self.create_message)(f'Створив чат з тобою!', chat.pk)).content
                }
            }
        }

        join_group_message = {
            'type': 'join_group',
            'message': {
                'group_name': group_name,
            }
        }
        
        await self.channel_layer.send(str(participant_channel_name), join_group_message)
        await self.channel_layer.group_send(group_name, message)

    async def send_online_status(self, online_status):
        message = {
            'type': 'chat_message',
            'action': 'online_status',
            'message': {
                "user": {
                    'pk': self.user.pk,
                    'username': self.user.username,
                },
                'online_status': online_status
            }
        }   
        for chat in self.chats:
            await self.channel_layer.group_send(chat, message)

    async def send_typing_status(self, chat, typing_status):
        message = {
            'type': 'chat_message',
            'action': 'typing_status',
            'message': {
                'user': {
                    'pk': self.user.pk,
                    'username': self.user.username
                },
                'typing_status': typing_status
            }
        }
        await self.channel_layer.group_send(chat, message)

    async def send_messages(self, chat):
        messages_qs = await database_sync_to_async(lambda: Message.objects.filter(chat=chat).order_by('created_at'))()
        messages = []
        async for message in messages_qs:
            messages.append({
                'pk': message.pk,
                'author_avatar': await database_sync_to_async(lambda: message.author.avatar.url)(),
                'author': await database_sync_to_async(lambda: message.author.username)(),
                'content': message.content,
                'chat': await database_sync_to_async(lambda:  message.chat.pk)(),
                'created_at': str(message.created_at)
            })
        message = {
            'action': 'get_messages',
            'message': {
                'messages': messages
            }
        }
        await self.send(text_data=json.dumps(message))

    async def send_user_suggestions(self, username):
        users_qs = await database_sync_to_async(lambda: CustomUser.objects.filter(username__startswith=username).exclude(pk=self.user.pk))()
        users = []
        async for user in users_qs:
            users.append({
                'pk': user.pk,
                'username': user.username,
            })
        message = {
            'action': 'user_suggestions',
            'message': {
                'users': users
            } 
        }
        await self.send(text_data=json.dumps(message))

    async def listen_to_participated_chats(self):
        chats = await database_sync_to_async(self.get_chats)()
        self.chats = []

        async for chat in chats:
            group_name = f'chat_{chat.pk}'
            self.chats.append(group_name)
            await self.channel_layer.group_add(group_name, self.channel_name)

    async def join_group(self, event):
        message = event['message']
        self.chats.append(message['group_name'])

    async def connect(self):
        self.user = self.scope['user']

        await database_sync_to_async(self.change_user_online_status)(online_status=True)
        await self.listen_to_participated_chats()
        await self.send_online_status(online_status=True)
        
        await self.accept()
        
    async def disconnect(self, close_code):
        await database_sync_to_async(self.change_user_online_status)(online_status=False)
        await self.send_online_status(online_status=False)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        received_data = text_data_json
        action = received_data['action']
        message = received_data['message']
        print(received_data)

        # if action == 'auth':
        #     if received_data['token'] != 'connection':
        #         await self.close()
        #         return
        #     await self.send(json.dumps({"status": "authenticated"}))
        #     return

        if action == 'user_suggestions':
            await self.send_user_suggestions(message['username'])
        elif action == 'create_chat':
            await self.save_n_send_chat(message['participant_pk'])
        elif action == 'get_messages':
            await self.send_messages(message['chatpk'])
        elif action == 'typing_status':
            await self.send_typing_status(message['chatpk'], message['typing_status'])
        elif action == 'new_message':
            await self.save_n_send_message(message['chatpk'], message['content'])
        
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

