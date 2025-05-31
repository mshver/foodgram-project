from django.contrib import admin
from django.urls import include, path

# Основные URL-маршруты
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls', namespace='auth')),
    path('api/', include('api.urls', namespace='api'))
]