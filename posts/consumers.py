from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from .models import Comment
from django.core.files.base import ContentFile
import base64

class PostsConsumers(AsyncWebsocketConsumer):
    def get_comments(self, postpk):
        comments_qr = Comment.objects.filter(post_id=postpk)

        return comments_qr
    
    def create_comment(self, postpk, content, mediabase64, filename):
        if mediabase64:
            if mediabase64 and mediabase64.startswith("data:"):
                header, mediabase64 = mediabase64.split(",", 1)

            decoded_media = base64.b64decode(mediabase64)

        comment = Comment.objects.create(post_id=postpk,
                                         author=self.user,
                                         content=content,
                                         media=ContentFile(decoded_media, filename) if mediabase64 else None)
        
        return comment

    async def send_comments(self, postpk):
        comments_qr = await database_sync_to_async(self.get_comments)(postpk)
        comments = []

        async for comment in comments_qr:
            comments.append({
                'pk': comment.pk,
                'author_pk': await database_sync_to_async(lambda: comment.author.pk)(),
                'author_avatar': await database_sync_to_async(lambda: comment.author.avatar.url)(),
                'author_username': await database_sync_to_async(lambda: comment.author.username)(),
                'content': comment.content,
                'media': await database_sync_to_async(lambda: comment.media.url if comment.media else None)(),
                'likes': await database_sync_to_async(lambda: len(comment.likes.all()))(),
                'created_at': str(comment.created_at)
            })

        await self.send(text_data=json.dumps({
                'action': 'get_comments',
                'message': {
                    'comments': comments,
                    'postpk': postpk
                }
            }))
        
    async def save_n_send_comment(self, postpk, content, mediabase64, filename):
        comment = await database_sync_to_async(self.create_comment)(postpk, content, mediabase64, filename)

        await self.send(json.dumps({
            'action': 'create_comment',
            'message': {
                'comment': {
                    'pk': comment.pk,
                    'author_avatar': await database_sync_to_async(lambda: comment.author.avatar.url)(),
                    'author_username': await database_sync_to_async(lambda: comment.author.username)(),
                    'content': comment.content,
                    'media': await database_sync_to_async(lambda: comment.media.url if comment.media else None)(),
                    'likes': await database_sync_to_async(lambda: len(comment.likes.all()))(),
                    'created_at': str(comment.created_at)
                }
            }
        }))

    async def connect(self):
        self.user = self.scope['user']

        await self.accept()

    async def disconnect(self, code):
        pass

    async def receive(self, text_data):
        received_data = json.loads(text_data)
        action = received_data['action']
        message = received_data['message']
        print(received_data)

        if action == 'get_comments':
            await self.send_comments(message['postpk'])
        elif action == 'create_comment':
            await self.save_n_send_comment(message['postpk'], message['content'], message['media'], message['filename'])
