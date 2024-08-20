import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatApp.settings')
django.setup()

print("Django settings are configured correctly!")

