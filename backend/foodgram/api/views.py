from api.serializers import (FavoriteRecipeSerializer, IngredientSerializer,
                             RecipeCreateUpdateSerializer,
                             RecipeReadSerializer, ShoppingCartSerializer,
                             SubscriptionCreateSerializer,
                             SubscriptionReadSerializer, TagSerializer)
from django.db.models import Exists, OuterRef
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (FavoriteRecipe, Ingredient, IngredientRecipeAmount,
                            Recipe, ShoppingCart, Tag)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.models import Subscription, User

from .filters import RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .viewset import CreateDestroyView


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для ингредиента чтение"""

    queryset = Ingredient.objects.all()
    filter_backends = [filters.SearchFilter]
    serializer_class = IngredientSerializer
    search_fields = ['^name']
    pagination_class = None
    permission_classes = [AllowAny]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для тэга чтение"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [AllowAny]


class RecipeViewSet(viewsets.ModelViewSet):
    """Recipe CRUD"""

    queryset = Recipe.objects.all().order_by('-created_at')
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = RecipeFilter
    ordering_fields = ['-created_at']
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    @action(detail=False)
    def download_shopping_cart(self, request):
        """Скачиваем список покупок"""
        user = request.user
        shopping_cart_items = ShoppingCart.objects.filter(
            user=user
        ).select_related('shopping_recipe')

        shopping_cart = {}

        for item in shopping_cart_items:
            recipe = item.shopping_recipe
            ingredient_amounts = IngredientRecipeAmount.objects.filter(
                recipe=recipe
            )

            for ingrefient_amount in ingredient_amounts:
                ingredient = ingrefient_amount.ingredient
                name = ingredient.name
                amount = ingrefient_amount.amount
                unit = ingredient.measurement_unit

                if name in shopping_cart:
                    shopping_cart[name]['amount'] += amount
                else:
                    shopping_cart[name] = {'amount': amount, 'unit': unit}
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=shopping_cart.txt'

        for name, data in shopping_cart.items():
            response.write(f"{name} ({data['unit']}) — {data['amount']}\n")
        return response
    
    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH', 'DELETE']:
            return RecipeCreateUpdateSerializer
        elif self.request.method == 'GET':
            return RecipeReadSerializer
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Recipe.objects.annotate(is_in_shopping_cart=Exists(ShoppingCart.objects.filter(
            user=user, shopping_recipe=OuterRef('id'))), is_favorited=Exists(FavoriteRecipe.objects.filter(
            user=user, recipe=OuterRef('id')
            ))).order_by('-created_at')
        return Recipe.objects.all().order_by('-created_at')


class BaseRecipeActionView(CreateDestroyView):
    """Базовый класс для представлений Избранного и Списка покупок."""

    def get_lookup_field(self):
        raise NotImplementedError("Метод get_lookup_field должен быть переопределен")

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        recipe_id = self.kwargs['recipe_id']

        try:
            recipe_item = self.queryset.get(
                **{self.get_lookup_field(): recipe_id, 'user': user }
            )
            recipe_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except self.queryset.model.DoesNotExist:
            return Response(
                {'error': f'Рецепта нет в {self.queryset.model._meta.verbose_name}'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class FavoriteRecipeView(BaseRecipeActionView):
    """Представление для Избранного."""

    lookup_field = 'recipe_id'

    def get_lookup_field(self):
        return self.lookup_field

    queryset = FavoriteRecipe.objects.all()
    serializer_class = FavoriteRecipeSerializer
    permission_classes = [IsAuthenticated]


class ShoppingCartCreateView(BaseRecipeActionView):
    """Добавления/удаления рецепта из Списка покупок."""

    lookup_field = 'shopping_recipe_id'

    def get_lookup_field(self):
        return self.lookup_field

    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer


class SubscriptionsReadView(viewsets.ReadOnlyModelViewSet):
    """Представление просмотр подсписок"""

    serializer_class = SubscriptionReadSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = (
            Subscription.objects.filter(subscriber=user)
            .select_related('author')
            .order_by('pk')
        )
        return queryset


class SubscriptionsCreateView(CreateDestroyView):
    """Представление для Подписки/Отписки на пользователя"""

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionCreateSerializer
    lookup_field = 'author_id'

    def destroy(self, request, *args, **kwargs):
        subscriber = self.request.user
        author_id = self.kwargs['author_id']
        author = get_object_or_404(User, id=author_id)
        try:
            subscription = Subscription.objects.get(
                subscriber=subscriber, author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Subscription.DoesNotExist:
            return Response(
                {'error': 'Вы не были подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST,
            )
