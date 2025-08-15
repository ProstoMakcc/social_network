from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    avatar = models.ImageField(default='default.png', upload_to='avatars/')
    bio = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    followers = models.ManyToManyField('self', symmetrical=False)

    def __str__(self):
        return self.username

class OnlineUser(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    channel_name = models.TextField(default="")

    def __str__(self):
        return self.user.username

