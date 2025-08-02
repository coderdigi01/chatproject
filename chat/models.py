from django.contrib.auth.models import User
from django.db import models

class ChatGroup(models.Model):
    name = models.CharField(max_length=255, unique=True)
    members = models.ManyToManyField(User, related_name='chat_groups')

    def __str__(self):
        return self.name

class Message(models.Model):
    group = models.ForeignKey(ChatGroup, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.content[:20]}'
