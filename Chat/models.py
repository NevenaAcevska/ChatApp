from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} to {self.recipient} at {self.content}"

    @staticmethod
    def delete_old_messages():
        one_month_ago = timezone.now() - timedelta(days=30)
        print(f"Deleting messages older than: {one_month_ago}")
        old_messages = Message.objects.filter(timestamp__lt=one_month_ago)
        print(f"Found {old_messages.count()} old messages.")
        old_messages.delete()
