from rest_framework import serializers
from rest_framework import status
from backend.foodgram.recipes.models import FavoriteRecipe, Ingredient, IngredientRecipeAmount, Recipe, Tag
from validators import validate

from backend.foodgram.users.models import Subscription, User


class IngredientM2MSerializer(serializers.ModelSerializer):
    ingredient = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        
        model = IngredientRecipeAmount
        fields = ('ingredient', 'amount')
        read_only_fields = ('ingredient',)


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериалайзер Рецепт Получить"""
    class Meta:
        model = Recipe

        fields = '__all__'


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериалайзер Рецепт Создание, Обновление"""
    ingredients = IngredientM2MSerializer(many=True, source='ingredient_used', required=True)
    
    class Meta:

        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text', 'cooking_time', 'author')
        # серик не ждет от пост запроса это поле, а сам подставит при создании
        read_only_fields = ('author',)
    
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            current_ingredient, status = Ingredient.objects.get_or_create(**ingredient)
        
        IngredientRecipeAmount.objects.create(recipe=recipe, ingredient=current_ingredient)

        return recipe
    
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        # обновляем рецепт полученными данными
        for attr, value  in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        # создаем или берем ингредиент
        for ingredient in ingredients:
            current_ingredient, status = Ingredient.objects.get_or_create(**ingredient)
        # вяжем с рецептом
        IngredientRecipeAmount.objects.create(recipe=instance, ingredient=current_ingredient)

        return instance


class RecipeUserSerializer(serializers.ModelSerializer):
    """Сериализатор Рецепта для вложения в UserRecipeSerializer"""

    class Meta:
        
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор User с recipe для вложения в SubscriptionSerializer"""
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeUserSerializer(many=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_subscribed', 'recipes')

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
    # id = serializers.RecipeUserSerializer(source='recipe')

    class Meta:
        model = FavoriteRecipe
        fields = ('id', )
    # не факт что нужно описывать метод добавления
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
    # Нужен ли вообще метод делит, возможно хватит дэфолтного
    def delete(self, validated_data):
        id = validated_data.get('id')
        user = self.context['request'].user

        try:
            favorite_recipe = FavoriteRecipe.objects.get(recipe=id, user=user)
        except FavoriteRecipe.DoesNotExist:
            raise serializers.ValidationError('Рецепт не найден в избранном', status=status.HTTP_404_NOT_FOUND)

        favorite_recipe.delete()