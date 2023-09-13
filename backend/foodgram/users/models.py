from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя"""
    username = models.CharField(max_length=150, unique=True, blank=False)
    email = models.EmailField(
        unique=True, blank=False, null=False, max_length=254
    )
    first_name = models.CharField(
        max_length=150, blank=False, verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150, blank=False, verbose_name='Фамилия'
    )


class Subscription(models.Model):
    """Модель подписки на пользователя"""
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name='subscriptions')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='subscribers')

    class Meta:
        unique_together = ('subscriber', 'author')

    def __str__(self):
        return f"{self.subscriber} follows {self.author}"
