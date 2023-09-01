from rest_framework import serializers
from rest_framework import status
from backend.foodgram.recipes.models import FavoriteRecipe, Recipe, Tag
from validators import validate

from backend.foodgram.users.models import Subscription, User


class RecipeUserSerializer(serializers.ModelSerializer):
    """Сериализатор Рецепта для вложения в UserRecipeSerializer"""

    class Meta:
        
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор User с recipe для вложения в SubscriptionSerializer"""
    is_subscribed = serializers.SerializerMethodField()
    recipe = RecipeUserSerializer(many=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_subscribed', 'recipe')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        subscription_exist = Subscription.objects.filter(subscriber=user, author=obj).exists()
        return subscription_exist
    

class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписки"""
    # В выдачу добавляются рецепты 
    author = serializers.UserRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('author',)
    
    def get_recipes_count(self, obj):
        user = self.context['request'].user
        recipes_count = Recipe.objects.filter(author=user).count()
        return recipes_count

 
class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name', 'is_subscribed')
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        subscription_exist = Subscription.objects.filter(subscriber=user, author=obj).exists()
        return subscription_exist

    def validate(self, data):
        validate(self, data)
        return super().validate(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тэга"""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор Избранные рецепты"""
    id = serializers.RecipeUserSerializer(source='recipe')

    class Meta:
        model = FavoriteRecipe
        fields = ('id', )

    def create(self, validated_data):
        id = validated_data.get('id')
        user = self.context['request'].user
        # проверяем существование рецепта
        try:
            recipe = Recipe.objects.get(id=id)
        except Recipe.DoesNotExist:
            raise serializers.ValidationError('Рецепт с указанным id не существует')
        # проверяем не находится ли он уже в избранном
        if FavoriteRecipe.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError('Рецепт уже в избранном', status=status.HTTP_400_BAD_REQUEST)
        # добавляем в избранное
        FavoriteRecipe.objects.create(recipe=recipe, user=user)
        # возвращаем данные рецепта
        serialized_recipe = RecipeUserSerializer(recipe, context=self.context).data
        
        return serialized_recipe

    def delete(self, validated_data):
        id = validated_data.get('id')
        user = self.context['request'].user

        try:
            favorite_recipe = FavoriteRecipe.objects.get(recipe=id, user=user)
        except FavoriteRecipe.DoesNotExist:
            raise serializers.ValidationError('Рецепт не найден в избранном', status=status.HTTP_404_NOT_FOUND)

        favorite_recipe.delete()