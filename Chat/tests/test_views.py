from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

from Chat.models import Message


class ChatPageTest(TestCase):

    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username="testuser1", password="testpass1")
        self.user2 = User.objects.create_user(username="testuser2", password="testpass2")

        # Create some test messages
        self.message1 = Message.objects.create(
            sender=self.user1,
            recipient=self.user2,
            content="Hello, how are you?",
            timestamp=timezone.now() - timedelta(days=15)
        )
        self.message2 = Message.objects.create(
            sender=self.user2,
            recipient=self.user1,
            content="I am good, thanks!",
            timestamp=timezone.now() - timedelta(days=10)
        )

        Message.objects.filter(id=self.message1.id).update(timestamp=timezone.now() - timedelta(days=15))
        Message.objects.filter(id=self.message2.id).update(timestamp=timezone.now() - timedelta(days=10))

        self.recent_message = Message.objects.create(
            sender=self.user1,
            recipient=self.user2,
            content="Hello, how are you?",
            timestamp=timezone.now() - timedelta(days=5)
        )

        # Create an older message that should not be included
        self.old_message = Message.objects.create(
            sender=self.user1,
            recipient=self.user2,
            content="This is an old message",
            timestamp=timezone.now() - timedelta(days=30)
        )

        Message.objects.filter(id=self.recent_message.id).update(timestamp=timezone.now() - timedelta(days=5))

        Message.objects.filter(id=self.old_message.id).update(timestamp=timezone.now() - timedelta(days=30))
        # Create an instance of the test client
        self.client = Client()

    def test_chat_page_redirect_if_not_logged_in(self):
        # Attempt to access the chat page without being logged in
        response = self.client.get(reverse('chat-page'))
        # Verify that the response redirects to the login page
        self.assertRedirects(response, reverse('login-user'))

    def test_chat_page_logged_in_user(self):
        # Log in the user
        self.client.login(username="testuser1", password="testpass1")

        # Access the chat page
        response = self.client.get(reverse('chat-page'))

        # Verify that the request was successful
        self.assertEqual(response.status_code, 200)
        # Verify that the messages are in the context
        self.assertIn(self.message1, response.context['messages'])
        self.assertIn(self.message2, response.context['messages'])

    def test_messages_filtered_by_timestamp(self):
        # Log in the user
        self.client.login(username="testuser1", password="testpass1")

        # Access the chat page
        response = self.client.get(reverse('chat-page'))
        for msg in response.context['messages']:
            print(f"Message: {msg.content}, Timestamp: {msg.timestamp}")

        # Verify that the recent message is included in the context
        self.assertIn(self.recent_message, response.context['messages'])

        # Verify that the old message is not in the context
        self.assertNotIn(self.old_message, response.context['messages'])


class UserListTest(TestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username="testuser1", password="testpass1")
        self.user2 = User.objects.create_user(username="anotheruser", password="testpass2")
        self.client = Client()

    def test_user_list_ajax_request(self):
        # Simulate an AJAX request with a search term
        response = self.client.get(reverse('user_list'), {'term': 'test'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        # Verify the response status
        self.assertEqual(response.status_code, 200)

        # Verify the JSON response
        self.assertJSONEqual(response.content, ['testuser1'])

    def test_user_list_non_ajax_request(self):
        # Simulate a non-AJAX request
        response = self.client.get(reverse('user_list'), {'term': 'test'})

        # Verify that the response is empty since it is not an AJAX request
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, '[]')
