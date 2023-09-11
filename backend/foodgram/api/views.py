from rest_framework import viewsets
from api.serializers import IngredientSerializer, TagSerializer, RecipeSerializer, UserSerializer
from rest_framework.permissions import AllowAny
from recipes.models import Ingredient, Tag, Recipe
from users.models import User


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


# class UserViewSet(viewsets.ReadOnlyModelViewSet):
#     """Представление для пользователей чтение"""
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
