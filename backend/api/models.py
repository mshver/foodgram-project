from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models

UserModel = get_user_model()

class Component(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название компонента')
    unit = models.CharField(max_length=200, verbose_name='Единица измерения')

    class Meta:
        ordering = ['-id']
        verbose_name = 'Компонент'
        verbose_name_plural = 'Компоненты'
        constraints = [
            models.UniqueConstraint(fields=['title', 'unit'], name='unique_component')
        ]

    def __str__(self):
        return self.title

class Category(models.Model):
    BLUE_HEX = '#0000FF'
    ORANGE_HEX = '#FFA500'
    GREEN_HEX = '#008000'
    PURPLE_HEX = '#800080'
    YELLOW_HEX = '#FFFF00'

    COLOR_OPTIONS = [
        (BLUE_HEX, 'Синий'),
        (ORANGE_HEX, 'Оранжевый'),
        (GREEN_HEX, 'Зеленый'),
        (PURPLE_HEX, 'Фиолетовый'),
        (YELLOW_HEX, 'Желтый'),
    ]
    
    title = models.CharField(max_length=200, unique=True, verbose_name='Название категории')
    hex_code = models.CharField(max_length=7, unique=True, choices=COLOR_OPTIONS, verbose_name='Цвет в HEX')
    url_slug = models.SlugField(max_length=200, unique=True, verbose_name='URL-идентификатор')

    class Meta:
        ordering = ['-id']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title

class Dish(models.Model):
    creator = models.ForeignKey(
        UserModel, 
        on_delete=models.CASCADE,
        related_name='dishes',
        verbose_name='Автор рецепта'
    )
    title = models.CharField(max_length=200, verbose_name='Название рецепта')
    image = models.ImageField(upload_to='dishes/', verbose_name='Изображение')
    description = models.TextField(verbose_name='Описание')
    components = models.ManyToManyField(
        Component,
        through='ComponentQuantity',
        verbose_name='Компоненты',
        related_name='dishes',
    )
    categories = models.ManyToManyField(
        Category,
        verbose_name='Категории',
    )
    duration = models.PositiveSmallIntegerField(
        validators=[validators.MinValueValidator(1, message='Минимальное время 1 минута')],
        verbose_name='Время приготовления'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

class ComponentQuantity(models.Model):
    component = models.ForeignKey(
        Component,
        on_delete=models.CASCADE,
        verbose_name='Компонент',
    )
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    quantity = models.PositiveSmallIntegerField(
        validators=[validators.MinValueValidator(1, message='Минимальное количество 1')],
        verbose_name='Количество',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Количество компонента'
        verbose_name_plural = 'Количества компонентов'
        constraints = [
            models.UniqueConstraint(fields=['component', 'dish'], name='unique_component_per_dish')
        ]

class Bookmark(models.Model):
    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(fields=['user', 'dish'], name='unique_user_bookmark')
        ]

class ShoppingCart(models.Model):
    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name='Пользователь',
    )
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
        related_name='in_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(fields=['user', 'dish'], name='unique_cart_item')
        ]