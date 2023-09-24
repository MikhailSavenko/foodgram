from django_filters import rest_framework as filters
from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    tags = filters.CharFilter(
        field_name='tags__slug', method='filter_tags', required=False
    )
    author = filters.NumberFilter(field_name='author__id')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    def filter_tags(self, queryset, name, value):
        if self.request.user.is_authenticated:
            return queryset.filter(tags__slug=value)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value:
                # залазим в модель FavoriteRecipe
                return queryset.filter(favoriterecipe__user=user)
            return queryset
        return queryset.none()

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value:
                # залазим в модель ShooppingCart
                return queryset.filter(shoppingcart__user=user)
            return queryset
        return queryset.none()

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']
