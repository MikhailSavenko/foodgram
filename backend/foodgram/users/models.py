from django.contrib.auth.models import AbstractUser
from django.db import models
# from foodgram.recipes.models import Recipe
from django.contrib.auth.hashers import check_password, make_password


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
    password = models.CharField(max_length=150, blank=False,
                                verbose_name='Пароль')

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


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


class FavoriteRecipe(models.Model):
    """Модель избранное"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


class ShoppingCart(models.Model):
    """Модель список покупок"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shopping_recipe = models.ManyToManyField(Recipe)
