from django.db import models
from auth_system.models import CustomUser

class Post(models.Model):
    description = models.TextField()
    media = models.ImageField(upload_to='posts_media')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    likes = models.ManyToManyField(CustomUser, related_name='post_likes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f'Post from {self.author} with description: {self.description}'

class Comment(models.Model):
    content = models.TextField()
    media = models.ImageField(upload_to='comments_media')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    likes = models.ManyToManyField(CustomUser, related_name='comment_likes', blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f'Comment from {self.author} with content: {self.content}'
