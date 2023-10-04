from api.views import (FavoriteRecipeView, IngredientViewSet, RecipeViewSet,
                       ShoppingCartCreateView, SubscriptionsCreateView,
                       SubscriptionsReadView, TagViewSet)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = 'api'

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')


urlpatterns = [
    path('', include(router.urls)),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        ShoppingCartCreateView.as_view(
            actions={'post': 'create', 'delete': 'destroy'}
        ),
    ),
    path(
        'users/subscriptions/',
        SubscriptionsReadView.as_view(actions={'get': 'list'}),
    ),
    path(
        'users/<int:author_id>/subscribe/',
        SubscriptionsCreateView.as_view(
            actions={'post': 'create', 'delete': 'destroy'}
        ),
    ),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'recipes/<int:recipe_id>/favorite/',
        FavoriteRecipeView.as_view(
            actions={'post': 'create', 'delete': 'destroy'}
        ),
        name='favorite-recipe',
    ),
]
