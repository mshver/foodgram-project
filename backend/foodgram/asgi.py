import os
from django.core.asgi import get_asgi_application

# Установка переменной окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')

# Получение ASGI-приложения
asgi_app = get_asgi_application()