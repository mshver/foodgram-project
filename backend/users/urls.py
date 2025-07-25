from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet

api_name = 'user_api'

router = DefaultRouter()
router.register('profiles', UserProfileViewSet, basename='profiles')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]