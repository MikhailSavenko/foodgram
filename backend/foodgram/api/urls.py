from api.views import IngredientViewSet, TagViewSet, RecipeViewSet, FavoriteRecipeView, SubscriptionsReadView, SubscriptionsCreateView, ShoppingCartCreateView, download_shopping_cart
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from django.conf import settings
from django.conf.urls.static import static

app_name = 'api'

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('recipes/download_shopping_cart/', download_shopping_cart, name='download_shopping_cart'),
    path('recipes/<int:recipe_id>/shopping_cart/', ShoppingCartCreateView.as_view(actions={'post': 'create', 'delete':'destroy'})),
    path('users/subscriptions/', SubscriptionsReadView.as_view(actions={'get': 'list'})),
    path('users/<int:author_id>/subscribe/', SubscriptionsCreateView.as_view(actions={'post': 'create', 'delete':'destroy'})),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('recipes/<int:recipe_id>/favorite/', FavoriteRecipeView.as_view(actions={'post': 'create', 'delete': 'destroy'}), name='favorite-recipe'),
    path('', include(router.urls)),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)