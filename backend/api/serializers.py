from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from api.models import Component, ComponentQuantity, Dish, Category
from users.models import Subscription
from users.serializers import CustomUserSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Component
        fields = '__all__'

class ComponentDetailSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='component.id')
    title = serializers.ReadOnlyField(source='component.title')
    unit = serializers.ReadOnlyField(source='component.unit')

    class Meta:
        model = ComponentQuantity
        fields = ('id', 'title', 'unit', 'quantity')

class DishSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    categories = CategorySerializer(read_only=True, many=True)
    creator = CustomUserSerializer(read_only=True)
    components = ComponentDetailSerializer(
        source='componentquantity_set',
        many=True,
        read_only=True,
    )
    is_bookmarked = serializers.SerializerMethodField()
    in_cart = serializers.SerializerMethodField()

    class Meta:
        model = Dish
        fields = ('id', 'categories', 'creator', 'components', 'is_bookmarked',
                  'in_cart', 'title', 'image', 'description', 'duration')

    def get_is_bookmarked(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated and 
                Dish.objects.filter(bookmarks__user=user, id=obj.id).exists())

    def get_in_cart(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated and 
                Dish.objects.filter(in_cart__user=user, id=obj.id).exists())

    def validate(self, data):
        components_data = self.initial_data.get('components')
        if not components_data:
            raise serializers.ValidationError(
                {'components': 'Требуется хотя бы один компонент'}
            )
        
        seen_components = set()
        for comp in components_data:
            comp_id = comp['id']
            if comp_id in seen_components:
                raise serializers.ValidationError(
                    'Компоненты должны быть уникальными'
                )
            seen_components.add(comp_id)
            
            if int(comp['quantity']) <= 0:
                raise serializers.ValidationError(
                    {'components': 'Количество должно быть положительным числом'}
                )
        data['components'] = components_data
        return data

    def create_components(self, components, dish):
        ComponentQuantity.objects.bulk_create([
            ComponentQuantity(
                dish=dish,
                component_id=comp['id'],
                quantity=comp['quantity'],
            ) for comp in components
        ])

    def create(self, validated_data):
        image = validated_data.pop('image')
        components_data = validated_data.pop('components')
        dish = Dish.objects.create(image=image, **validated_data)
        dish.categories.set(self.initial_data.get('categories'))
        self.create_components(components_data, dish)
        return dish

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.duration = validated_data.get('duration', instance.duration)
        
        instance.categories.clear()
        categories_data = self.initial_data.get('categories')
        instance.categories.set(categories_data)
        
        ComponentQuantity.objects.filter(dish=instance).delete()
        self.create_components(validated_data.get('components'), instance)
        
        instance.save()
        return instance

class DishPreviewSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Dish
        fields = ('id', 'title', 'image', 'duration')
        read_only_fields = fields

class SubscriptionSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    dishes = serializers.SerializerMethodField()
    dish_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'dishes', 'dish_count')

    def get_is_subscribed(self, obj):
        return Subscription.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_dishes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('dishes_limit')
        queryset = Dish.objects.filter(creator=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return DishPreviewSerializer(queryset, many=True).data

    def get_dish_count(self, obj):
        return Dish.objects.filter(creator=obj.author).count()