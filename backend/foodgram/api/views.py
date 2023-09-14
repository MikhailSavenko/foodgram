from rest_framework.response import Response
from rest_framework import viewsets, status, mixins
from api.serializers import IngredientSerializer, TagSerializer, RecipeSerializer, FavoriteRecipeSerializer, SubscriptionReadSerializer, SubscriptionCreateSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from .viewset import CreateDestroyView
from recipes.models import Ingredient, Tag, Recipe, FavoriteRecipe
from users.models import User, Subscription
# from rest_framework.decorators import action


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


class FavoriteRecipeView(CreateDestroyView):
    """Представление для Избранного"""
    queryset = FavoriteRecipe.objects.all()
    serializer_class = FavoriteRecipeSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'recipe_id'


class SubscriptionsReadView(viewsets.ReadOnlyModelViewSet):
    """Представление просмотр подсписок"""
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionReadSerializer


class SubscriptionsCreateView(CreateDestroyView):
    """Представление для Подписки/Отписки на пользователя"""
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionCreateSerializer
    lookup_field = 'author_id'