# tasks.py
from celery import shared_task
from .models import Message


@shared_task
def delete_old_messages_task():
    Message.delete_old_messages()
