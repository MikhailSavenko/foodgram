from rest_framework import viewsets
from api.serializers import IngredientSerializer, TagSerializer, RecipeReadSerializer, RecipeCreateUpdateSerializer

from recipes.models import Ingredient, Tag, Recipe


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для ингредиента чтение"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для тэга чтение"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление Рецепт чтение, обновление, удаление"""
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        elif self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return RecipeCreateUpdateSerializer
        return super().get_serializer_class()