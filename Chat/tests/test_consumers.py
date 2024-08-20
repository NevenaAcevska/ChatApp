from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User
from django.test import TestCase
from ChatApp.asgi import application
from channels.db import database_sync_to_async
import json

class ChatConsumerTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", password="testpass1")
        self.user2 = User.objects.create_user(username="testuser2", password="testpass2")
        self.client.force_login(self.user1)
        self.cookie = self.client.cookies['sessionid'].value

    @database_sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)

    @database_sync_to_async
    def get_message(self, sender, recipient, content):
        from Chat.models import Message
        return Message.objects.get(sender=sender, recipient=recipient, content=content)

    async def test_connect_authenticated(self):
        communicator = WebsocketCommunicator(
            application,
            "ws/chat/",
            headers=[(b'cookie', f'sessionid={self.cookie}'.encode())]
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_connect_unauthenticated(self):
        communicator = WebsocketCommunicator(
            application,
            "ws/chat/"
        )
        connected, _ = await communicator.connect()
        self.assertFalse(connected)
        await communicator.disconnect()

    async def test_send_message(self):
        communicator = WebsocketCommunicator(
            application,
            "ws/chat/",
            headers=[(b'cookie', f'sessionid={self.cookie}'.encode())]
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_json_to({
            "action": "send",
            "message": "Hello, world!",
            "username": "testuser1",
            "recipient": "testuser2"
        })

        response = await communicator.receive_json_from()
        self.assertEqual(response["action"], "message")
        self.assertEqual(response["message"], "Hello, world!")
        self.assertEqual(response["username"], "testuser1")
        self.assertEqual(response["recipient"], "testuser2")

        message = await self.get_message(
            sender=self.user1,
            recipient=await self.get_user(username="testuser2"),
            content="Hello, world!"
        )
        self.assertIsNotNone(message)

        await communicator.disconnect()

    async def test_send_message_user_does_not_exist(self):
        communicator = WebsocketCommunicator(
            application,
            "ws/chat/",
            headers=[(b'cookie', f'sessionid={self.cookie}'.encode())]
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_json_to({
            "action": "send",
            "message": "Hello, world!",
            "username": "testuser1",
            "recipient": "nonexistentuser"
        })

        response = await communicator.receive_json_from()
        self.assertEqual(response["action"], "error")
        self.assertEqual(response["message"], "User does not exist")

        await communicator.disconnect()
