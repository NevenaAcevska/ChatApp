# celery.py
from celery import app
from celery.schedules import crontab


app.conf.beat_schedule = {
    'delete-old-messages-every-day': {
        'task': 'Chat.tasks.delete_old_messages_task',
        'schedule': crontab(hour=0, minute=0),
    },
}
