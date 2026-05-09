import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodconnect.settings')
django.setup()

from django.contrib.auth.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@bloodconnect.com',
        password='Admin1234!'
    )
    print("Superuser créé.")
else:
    print("Superuser existe déjà.")