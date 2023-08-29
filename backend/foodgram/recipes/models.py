from django.db import models
from django.utils.translation import gettext_lazy as _
from foodgram.users.models import User


class Recipe(models.Model):
    """Модель Рецепт"""
    author = models.ForeignKey(User, om_delete=models.CASCADE, blank=False)
    name = models.CharField(max_length=200, blank=False)
    ingredients = models.ManyToManyField(Ingredient, blank=False)
    tags = models.ManyToManyField(Tag, blank=False)
    text = models.TextField(blank=False)
    cooking_time = models.IntegerField(blank=False)
    image = models.BinaryField(blank=False)


class IngredientRecipeAmount(models.Model):
    """Промежуточная модель связи Рецепта Ингредиента с добавлением количества """
    recipe = models.ForeignKey(Recipe)
    ingredient = models.ForeignKey(Ingredient)
    amount = models.IntegerField()


class Ingredient(models.Model):
    """Модель Ингредиента"""
    name = models.CharField(max_length=200, db_index=True)
    measurement_unit = models.CharField(max_length=20)
    amount = models.ForeignKey(IngredientRecipeAmount)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель Тэг"""
    class Name(models.TextChoices):
        BREAKFAST = 'завтрак', _('Завтрак')
        LUNCH = 'обед', _('Обед')
        DINNER = 'ужин', _('Ужин')

    name = models.CharField(
        max_length=30, choices=Name.choices, blank=False, unique=True)
    
    color = models.CharField(max_length=20, blank=False, unique=True,)
    slug = models.SlugField(unique=True, blank=False)

    def __str__(self):
        return self.name


