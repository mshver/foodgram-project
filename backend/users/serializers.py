from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Subscription

UserModel = get_user_model()

class UserRegistrationSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=UserModel.objects.all())]
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=UserModel.objects.all())]
    )

    class Meta:
        model = UserModel
        fields = (
            'email', 'id', 'password', 'username', 
            'first_name', 'last_name'
        )
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'password': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

class UserProfileSerializer(UserSerializer):
    has_subscription = serializers.SerializerMethodField()

    class Meta:
        model = UserModel
        fields = (
            'email', 'id', 'username', 'first_name', 
            'last_name', 'has_subscription'
        )

    def get_has_subscription(self, instance):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            subscriber=request.user, 
            publisher=instance
        ).exists()