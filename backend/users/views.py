from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.pagination import LimitPageNumberPagination
from .serializers import SubscriptionSerializer
from .models import Subscription

UserModel = get_user_model()

class UserProfileViewSet(UserViewSet):
    pagination_class = LimitPageNumberPagination

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def follow(self, request, id=None):
        subscriber = request.user
        publisher = get_object_or_404(UserModel, id=id)

        if subscriber == publisher:
            return Response(
                {'error': 'Невозможно подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Subscription.objects.filter(subscriber=subscriber, publisher=publisher).exists():
            return Response(
                {'error': 'Подписка уже оформлена'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription = Subscription.objects.create(
            subscriber=subscriber, 
            publisher=publisher
        )
        serializer = SubscriptionSerializer(
            subscription, 
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @follow.mapping.delete
    def unfollow(self, request, id=None):
        subscriber = request.user
        publisher = get_object_or_404(UserModel, id=id)
        
        if subscriber == publisher:
            return Response(
                {'error': 'Невозможно отписаться от самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        subscription = Subscription.objects.filter(
            subscriber=subscriber, 
            publisher=publisher
        )
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'error': 'Подписка не найдена'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, permission_classes=[IsAuthenticated])
    def following(self, request):
        subscriber = request.user
        subscriptions = Subscription.objects.filter(subscriber=subscriber)
        paginated = self.paginate_queryset(subscriptions)
        serializer = SubscriptionSerializer(
            paginated,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)