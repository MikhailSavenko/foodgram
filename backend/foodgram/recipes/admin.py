from django.contrib import admin

from .models import (FavoriteRecipe, Ingredient, IngredientRecipeAmount,
                     Recipe, ShoppingCart, Tag)


class IngredientInline(admin.TabularInline):
    model = IngredientRecipeAmount


# class FavoriteRecipeInline(admin.TabularInline):
#     model = FavoriteRecipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientInline]
    list_display = ('name', 'author', 'recipe_in_favoriterecipe')
    list_filter = ('author', 'name', 'tags')

    def recipe_in_favoriterecipe(self, obj):
        return FavoriteRecipe.objects.filter(recipe=obj).count()

    recipe_in_favoriterecipe.admin_order_field = 'recipe_in_favoriterecipe'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    pass


@admin.register(IngredientRecipeAmount)
class IngredientRecipeAmountAdmin(admin.ModelAdmin):
    pass
