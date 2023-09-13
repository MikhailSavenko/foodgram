from rest_framework.response import Response
from rest_framework import viewsets, status
from api.serializers import IngredientSerializer, TagSerializer, RecipeSerializer
from rest_framework.permissions import AllowAny
from recipes.models import Ingredient, Tag, Recipe
from users.models import User
from rest_framework.decorators import action


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для ингредиента чтение"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для тэга чтение"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Recipe CRUD"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
# ДОБАВИТЬ ФИЛЬТРАЦИЮ!
# НАСТРОИТЬ PERMISSIONS

