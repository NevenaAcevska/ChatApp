import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from django.utils import timezone
from asgiref.sync import sync_to_async
from .models import Message
import logging

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'chat_room'

        # Check if the user is authenticated
        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()  # Close the connection if not authenticated

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')
        message = text_data_json.get('message')
        username = text_data_json.get('username')
        recipient_username = text_data_json.get('recipient')
        timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

        if action == 'send':
            if message and username and recipient_username:
                try:
                    sender = await sync_to_async(User.objects.get)(username=username)
                    recipient = await sync_to_async(User.objects.get)(username=recipient_username)

                    # Save the message to the database
                    message_obj = await sync_to_async(Message.objects.create)(
                        sender=sender,
                        recipient=recipient,
                        content=message,
                        timestamp=timestamp,
                    )

                    # Send the message to the group
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'send_message',
                            'message': message,
                            'username': username,
                            'recipient': recipient_username,
                            'timestamp': timestamp,
                            'message_id': message_obj.id
                        }
                    )
                except User.DoesNotExist:
                    logger.error(f"User does not exist: {username} or {recipient_username}")
                    # Optionally send an error message back to the user
                    await self.send(text_data=json.dumps({
                        'action': 'error',
                        'message': 'User does not exist'
                    }))

    async def send_message(self, event):
        message = event['message']
        username = event['username']
        recipient = event['recipient']
        timestamp = event['timestamp']
        message_id = event['message_id']

        # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            'action': 'message',
            'message': message,
            'username': username,
            'recipient': recipient,
            'timestamp': timestamp,
            'message_id': message_id
        }))
