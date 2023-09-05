from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User
from django.core.validators import MinValueValidator


class Ingredient(models.Model):
    """Модель Ингредиента"""
    name = models.CharField(max_length=200, db_index=True)
    measurement_unit = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель Тэг"""
    name = models.CharField(
        max_length=30, blank=False, unique=True)
    color = models.CharField(max_length=20, blank=False, unique=True,)
    slug = models.SlugField(unique=True, blank=False)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель Рецепт"""
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, 
                               related_name='recipes')
    name = models.CharField(max_length=200, blank=False)
    # установил blank True чтобы можно было создать рецепт без ингредиента в сериализаторе RecipeCreateUpdateSerializer
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientRecipeAmount',
                                         blank=True,
                                         related_name='recipes')
    tags = models.ManyToManyField(Tag, blank=False,
                                  related_name='recipes')
    text = models.TextField(blank=False)
    cooking_time = models.IntegerField(blank=False)
    image = models.BinaryField(blank=False)


class IngredientRecipeAmount(models.Model):
    """Промежуточная модель связи Рецепта Ингредиента с добавлением количества """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredient_used') # может есть смысл в related_name = amount для сериализатора 
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='recipe_used')
    amount = models.IntegerField(blank=False, default=1,
                                 validators=[MinValueValidator(1)])


class FavoriteRecipe(models.Model):
    """Модель избранное"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


class ShoppingCart(models.Model):
    """Модель список покупок"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shopping_recipe = models.ManyToManyField(Recipe, related_name='shopping_cart')