from django.contrib.auth import get_user_model
from django.db import models

UserModel = get_user_model()

class Subscription(models.Model):
    subscriber = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик',
    )
    publisher = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор контента',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'publisher'],
                name='unique_subscription',
            )
        ]