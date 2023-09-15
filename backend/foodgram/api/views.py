from rest_framework.response import Response
from rest_framework import viewsets, status, mixins
from api.serializers import IngredientSerializer, TagSerializer, RecipeSerializer, FavoriteRecipeSerializer, SubscriptionReadSerializer, SubscriptionCreateSerializer, ShoppingCartSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from .viewset import CreateDestroyView
from recipes.models import Ingredient, Tag, Recipe, FavoriteRecipe, ShoppingCart, IngredientRecipeAmount
from users.models import User, Subscription
from django.http import HttpResponse
# from rest_framework.decorators import action


def download_shopping_cart(request):
    """Скачиваем список покупок"""
    user = request.user
    print(user)
    shopping_cart_items = ShoppingCart.objects.filter(user=user).select_related('shopping_recipe')

    shopping_cart = {}

    for item in shopping_cart_items:
        recipe = item.shopping_recipe
        ingredient_amounts = IngredientRecipeAmount.objects.filter(recipe=recipe)

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
    response['Content-Disposition'] = f'attachment; filename=shopping_cart.txt'

    for name, data in shopping_cart.items():
        response.write(f"{name} ({data['unit']}) — {data['amount']}\n")

    return response


class ShoppingCartCreateView(CreateDestroyView):
    """Добавления/удаления рецепта из Списка покупок"""
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    lookup_field = 'recipe_id'

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        recipe_id = self.kwargs['recipe_id']

        try:
            shopping_cart_recipe = ShoppingCart.objects.get(shopping_recipe=recipe_id, user=user)
            shopping_cart_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ShoppingCart.DoesNotExist:
            return Response({'error': 'Рецепта нет в списке покупок'}, status=status.HTTP_400_BAD_REQUEST)


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
    
    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        recipe_id = self.kwargs['recipe_id']

        try:
            favorite_recipe = FavoriteRecipe.objects.get(recipe=recipe_id, user=user)
            favorite_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FavoriteRecipe.DoesNotExist:
            return Response({'error': 'Рецепта нет в избранном'}, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionsReadView(viewsets.ReadOnlyModelViewSet):
    """Представление просмотр подсписок"""
    serializer_class = SubscriptionReadSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Subscription.objects.filter(subscriber=user).select_related('author')
        return queryset

       
class SubscriptionsCreateView(CreateDestroyView):
    """Представление для Подписки/Отписки на пользователя"""
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionCreateSerializer
    lookup_field = 'author_id'

    def destroy(self, request, *args, **kwargs):
        subscriber = self.request.user
        author_id = self.kwargs['author_id']

        try:
            subscription = Subscription.objects.get(subscriber=subscriber, author=author_id)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Subscription.DoesNotExist:
            return Response({'error': 'Вы не были подписаны на этого автора'}, status=status.HTTP_400_BAD_REQUEST)