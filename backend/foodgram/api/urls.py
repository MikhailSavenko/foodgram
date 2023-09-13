from api.views import IngredientViewSet, TagViewSet, RecipeViewSet, FavoriteRecipeView 
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = 'api'

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('recipes/<int:recipe_id>/favorite/', FavoriteRecipeView.as_view(actions={'post': 'create', 'delete': 'destroy'}), name='favorite-recipe'),
    path('', include(router.urls)),

]