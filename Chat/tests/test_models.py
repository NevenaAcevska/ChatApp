from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, datetime

from Chat.models import Message

now = timezone.now()
old = timezone.now() - timedelta(days=30)


class MessageModelTest(TestCase):

    def setUp(self):
        # Create users for testing
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')

        # Create messages for testing

        self.message_recent = Message.objects.create(
            sender=self.user1,
            recipient=self.user2,
            content='Recent message',
            timestamp=now
        )

        # Correctly set message_old to be 31 days old

        print(f"Calculated old timestamp: {old}")
        self.message_old = Message.objects.create(
            sender=self.user1,
            recipient=self.user2,
            content='Old message',
            timestamp=old
        )
        Message.objects.filter(id=self.message_old.id).update(timestamp=old)


    def test_message_creation(self):
        # Test that messages are created correctly
        self.assertEqual(self.message_recent.sender, self.user1)
        self.assertEqual(self.message_recent.recipient, self.user2)
        self.assertEqual(self.message_recent.content, 'Recent message')

    def test_message_string_representation(self):
        # Test the __str__ method
        expected_str = f"{self.user1} to {self.user2} at Recent message"
        self.assertEqual(str(self.message_recent), expected_str)

    def test_delete_old_messages(self):
        # Print the current time for debugging
        print(f"Current time: {now}")

        print(f"Old message: {self.message_old}")
        print(f"New message: {self.message_recent}")

        # Print timestamps of messages
        print(f"Recent message timestamp: {self.message_recent.timestamp}")
        print(f"Old message timestamp: {self.message_old.timestamp}")

        # Call the method to delete old messages
        Message.delete_old_messages()

        # Print remaining messages for debugging
        remaining_messages = Message.objects.all()
        for msg in remaining_messages:
            print(f"Remaining message: {msg.id} - {msg.timestamp}")


        # Verify that old messages are deleted
        self.assertFalse(Message.objects.filter(id=self.message_old.id).exists())

        # Verify that recent messages are not deleted
        self.assertTrue(Message.objects.filter(id=self.message_recent.id).exists())
