from rest_framework import viewsets
from api.serializers import IngredientSerializer

from recipes.models import Ingredient


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для ингредиентов чтение"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
