from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (FavoriteRecipe, Ingredient, IngredientRecipeAmount,
                            Recipe, ShoppingCart, Tag)
from rest_framework import serializers
from users.models import Subscription, User


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериалайзер Список покупок добавить/удалить"""

    id = serializers.PrimaryKeyRelatedField(
        source='shopping_recipe.id', read_only=True
    )
    name = serializers.StringRelatedField(
        source='shopping_recipe.name', read_only=True
    )
    image = serializers.ImageField(
        source='shopping_recipe.image', read_only=True
    )
    cooking_time = serializers.IntegerField(
        source='shopping_recipe.cooking_time', read_only=True
    )

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')

    def create(self, validated_data):
        recipe_id = self.context['view'].kwargs['recipe_id']
        user = self.context['request'].user
        try:
            recipe = Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            raise serializers.ValidationError(
                {'error': 'Рецепт с указанным id не существует'}
            )
        if ShoppingCart.objects.filter(
            shopping_recipe=recipe, user=user
        ).exists():
            raise serializers.ValidationError(
                {'error': 'Рецепт уже в списке покупок'}
            )
        # добавляем в избранное
        shopping_cart = ShoppingCart.objects.create(
            shopping_recipe=recipe, user=user
        )
        return shopping_cart


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер Ингредиент"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientM2MSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient'
    )
    measurement_unit = serializers.StringRelatedField(
        read_only=True, source='ingredient.measurement_unit'
    )
    name = serializers.StringRelatedField(
        read_only=True, source='ingredient.name'
    )

    class Meta:
        model = IngredientRecipeAmount
        fields = ('id', 'amount', 'measurement_unit', 'name')
        read_only_fields = ('ingredient',)


class UserReadSerializer(UserSerializer):
    """Сериализатор чтения пользователя"""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        read_only_fields = (
            'id',
            'is_subscribed',
            'username',
            'email',
            'first_name',
            'last_name',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            subscription_exist = Subscription.objects.filter(
                subscriber=user, author=obj
            ).exists()
            return subscription_exist
        return False


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя"""

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
        )
        read_only_fields = ('id',)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тэга"""
    
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('name', 'color', 'slug')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериалайзер Рецепт GET """

    ingredients = IngredientM2MSerializer(many=True, source='ingredient_used')
    author = UserReadSerializer(read_only=True)
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    tags = TagSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author',
            'is_favorited',
            'is_in_shopping_cart'
        )
        read_only_fields = (
            'id',
            'author',
            'is_favorited',
            'is_in_shopping_cart'
        )


class RecipeCreateUpdateSerializer(RecipeReadSerializer):
    """Сериалайзер Рецепт POST/PATCH/DEL"""
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )
        read_only_fields = (
            'id',
            'author',
            'is_favorited',
            'is_in_shopping_cart'
        )
    
    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredient_used')
        tags_data = validated_data.pop('tags')
        if not ingredients or not tags_data:
            raise serializers.ValidationError(
                {'error': 'Ингредиенты и теги обязательны для заполнения.'}
            )
        author = self.context['request'].user
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags_data)
        ingredient_data = []
        for ingredient in ingredients:
            current_ingredient = ingredient.get('ingredient')
            amount = ingredient.get('amount')
            ingredient_data.append(IngredientRecipeAmount(recipe=recipe, ingredient=current_ingredient, amount=amount))
        IngredientRecipeAmount.objects.bulk_create(ingredient_data)
        return recipe
    
    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredient_used')
        tags_data = validated_data.pop('tags')
        if not ingredients or not tags_data:
            raise serializers.ValidationError(
                {'error': 'Ингредиенты и теги обязательны для заполнения.'}
            )
        instance.tags.set(tags_data)
        instance.ingredients.clear()
        if ingredients:
            for ingredient in ingredients:
                current_ingredient = ingredient.get('ingredient')
                amount = ingredient.get('amount')
                instance.ingredients.add(
                    current_ingredient, through_defaults={'amount': amount}
                )
            instance.save()
        return super().update(instance, validated_data)


class RecipeUserSerializer(serializers.ModelSerializer):
    """Сериализатор Рецепта для вложения"""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionReadSerializer(serializers.ModelSerializer):
    """Сериализатор просмотр подписок"""

    id = serializers.StringRelatedField(source='author.id')
    email = serializers.StringRelatedField(source='author.email')
    username = serializers.StringRelatedField(source='author.username')
    first_name = serializers.StringRelatedField(source='author.first_name')
    last_name = serializers.StringRelatedField(source='author.last_name')
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'recipes',
            'recipes_count',
            'is_subscribed',
        )
        read_only_fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'recipes',
            'recipes_count',
            'is_subscribed',
        )

    def get_recipes_count(self, obj):
        user = obj.author
        recipes_count = Recipe.objects.filter(author=user).count()
        return recipes_count

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit'
        )
        user = obj.author
        if recipes_limit:
            recipes_limit = int(recipes_limit)
            recipes = Recipe.objects.filter(author=user).order_by(
                'created_at'
            )[:recipes_limit]
        else:
            recipes = Recipe.objects.filter(author=user).order_by('created_at')
        resipes = RecipeUserSerializer(recipes, many=True).data
        return resipes

    def get_is_subscribed(self, obj):
        author = obj.author
        user = self.context['request'].user
        subscription_exist = Subscription.objects.filter(
            subscriber=user, author=author
        ).exists()
        return subscription_exist


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор подписки/отписки"""

    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeUserSerializer(many=True, required=False)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        subscription_exist = Subscription.objects.filter(
            subscriber=user, author=obj
        ).exists()
        return subscription_exist

    def get_recipes_count(self, obj):
        author_id = self.context['view'].kwargs['author_id']
        recipes_count = Recipe.objects.filter(author=author_id).count()
        return recipes_count

    def create(self, validated_data):
        subscriber = self.context['request'].user
        author_id = self.context['view'].kwargs['author_id']
        if author_id == subscriber.id:
            raise serializers.ValidationError(
                {'error': 'На себя подписаться нельзя'}
            )
        try:
            author = get_object_or_404(User, id=author_id)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {'detail': 'Такого автора не существует'}
            )
        if Subscription.objects.filter(
            author=author, subscriber=subscriber
        ).exists():
            raise serializers.ValidationError(
                {'error': 'Вы уже подписаны на автора'}
            )
        Subscription.objects.create(author=author, subscriber=subscriber)
        return author


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор Избранные рецепты"""

    id = serializers.PrimaryKeyRelatedField(read_only=True, source='recipe.id')
    name = serializers.StringRelatedField(read_only=True, source='recipe.name')
    cooking_time = serializers.IntegerField(
        read_only=True, source='recipe.cooking_time'
    )
    image = serializers.ImageField(read_only=True, source='recipe.image')

    class Meta:
        model = FavoriteRecipe
        fields = ('id', 'name', 'cooking_time', 'image')
        read_only_fields = ('id', 'name', 'cooking_time', 'image')

    def create(self, validated_data):
        user = self.context['request'].user
        recipe_id = self.context['view'].kwargs['recipe_id']
        try:
            recipe = Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            raise serializers.ValidationError(
                {'error': 'Рецепт с указанным id не существует'}
            )
        if FavoriteRecipe.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError(
                {'error': 'Рецепт уже в избранном'}
            )
        favorite_recipe = FavoriteRecipe.objects.create(
            recipe=recipe, user=user
        )
        return favorite_recipe
