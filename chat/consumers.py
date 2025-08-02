from channels.db import database_sync_to_async
from .models import Group, Message
from django.contrib.auth.models import User
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        self.group_room = f"group_{self.group_name}"
        self.user = self.scope["user"]

        is_member = await self.is_user_in_group()
        if not is_member:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.group_room,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_room,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        await self.save_message(message)

        await self.channel_layer.group_send(
            self.group_room,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.user.username
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username']
        }))

    @database_sync_to_async
    def is_user_in_group(self):
        try:
            group = Group.objects.get(name=self.group_name)
            return group.members.filter(id=self.user.id).exists()
        except Group.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, message):
        group = Group.objects.get(name=self.group_name)
        return Message.objects.create(group=group, user=self.user, content=message)
