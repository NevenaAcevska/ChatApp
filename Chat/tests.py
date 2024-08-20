from django.test import TestCase

# Create your tests here.
import json
import pytest
from unittest.mock import patch
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User
from datetime import datetime
from asgiref.sync import sync_to_async

from Chat.consumers import ChatConsumer


@pytest.mark.asyncio
async def test_chat_consumer_send_message(mocker):
    # Create test users
    sender = await sync_to_async(User.objects.create)(username="sender")
    recipient = await sync_to_async(User.objects.create)(username="recipient")

    # Mock channel layer and message saving
    mock_channel_layer = mocker.patch('channels.layers.get_channel_layer')
    mock_message_save = mocker.patch('your_app.models.Message.objects.create')

    # Create a websocket communicator
    communicator = WebsocketCommunicator(ChatConsumer, '/ws/chat/')
    await communicator.connect()

    # Send a message
    await communicator.send_json_text({
        'action': 'send',
        'message': 'Hello',
        'username': 'sender',
        'recipient': 'recipient'
    })

    # Assertions
    assert mock_channel_layer.group_send.called
    assert mock_message_save.called
    assert mock_message_save.return_value.id in communicator.received_data[-1]['message_id']

    await communicator.disconnect()

@pytest.mark.asyncio
async def test_chat_consumer_handle_missing_user(mocker):
    # Mock channel layer and message saving
    mock_channel_layer = mocker.patch('channels.layers.get_channel_layer')
    mock_message_save = mocker.patch('your_app.models.Message.objects.create')

    # Create a websocket communicator
    communicator = WebsocketCommunicator(ChatConsumer, '/ws/chat/')
    await communicator.connect()

    # Send a message with non-existent user
    await communicator.send_json_text({
        'action': 'send',
        'message': 'Hello',
        'username': 'nonexistent',
        'recipient': 'recipient'
    })

    # Assertions
    assert not mock_channel_layer.group_send.called
    assert not mock_message_save.called

    await communicator.disconnect()
