from api.views import IngredientViewSet, TagViewSet, RecipeViewSet, FavoriteRecipeView, SubscriptionsReadView, SubscriptionsCreateView
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = 'api'

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('users/subscriptions/', SubscriptionsReadView.as_view(actions={'get': 'list'})),
    path('users/<int:author_id>/subscribe/', SubscriptionsCreateView.as_view(actions={'post': 'create', 'delete':'destroy'})),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('recipes/<int:recipe_id>/favorite/', FavoriteRecipeView.as_view(actions={'post': 'create', 'delete': 'destroy'}), name='favorite-recipe'),
    path('', include(router.urls)),

]