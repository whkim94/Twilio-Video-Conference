from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message
import json


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name


        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        user = self.scope['user']
        name = user.last_name + user.first_name

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': 'Entered',
                'speaker': user.username,
                'name': name
            }
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        user = self.scope['user']
        name = user.last_name + user.first_name

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': 'Exited',
                'speaker': user.username,
                'name': name
            }
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        speaker = text_data_json['speaker']
        name = text_data_json['name']

        # Save message to db
        await self.save_chat(speaker, name, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'speaker': speaker,
                'name': name
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        speaker = event['speaker']
        name = event['name']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'speaker': speaker,
            'name': name
        }))


    @database_sync_to_async
    def save_chat(self, speaker, name, message):
        room = Room.objects.get(group_name=self.room_name)
        return Message.objects.create(room=room, name=name, speaker=speaker, message=message)

    @database_sync_to_async
    def check_mentor(self, speaker):
        room = Room.objects.get(group_name=self.room_name)
        if speaker is not None and speaker == room.mentor:
            return 0
        else:
            return 1
