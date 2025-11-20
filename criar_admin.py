import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
USERNAME = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
EMAIL = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@admin.com')
PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=USERNAME).exists():
    print(f"Criando superusuário: {USERNAME}")
    User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
    print("Superusuário criado com sucesso!")
else:
    print(f"Superusuário {USERNAME} já existe.")