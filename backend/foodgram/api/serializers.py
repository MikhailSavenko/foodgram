from rest_framework import serializers
from rest_framework import status
from recipes.models import FavoriteRecipe, Ingredient, IngredientRecipeAmount, Recipe, ShoppingCart, Tag
from .validators import validate

from users.models import Subscription, User


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериалайзер Список покупок добавить/удалить"""
    
    class Meta:
        model = ShoppingCart
        fields = ('id', )

    def create(self, validated_data):
        id = validated_data.get('id')
        user = self.context['request'].user
        # проверяем существование рецепта
        try:
            recipe = Recipe.objects.get(id=id)
        except Recipe.DoesNotExist:
            raise serializers.ValidationError('Рецепт с указанным id не существует')
        # проверяем не находится ли он уже в 
        if ShoppingCart.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError('Рецепт уже в списке покупок', status=status.HTTP_400_BAD_REQUEST)
        # добавляем в избранное
        ShoppingCart.objects.create(recipe=recipe, user=user)
        # возвращаем данные рецепта
        serialized_recipe = RecipeUserSerializer(recipe, context=self.context).data
        return serialized_recipe
    
    def delete(self, validated_data):
        id = validated_data.get('id')
        user = self.context['request'].user

        try:
            shopping_cart_recipe = ShoppingCart.objects.get(recipe=id, user=user)
        except ShoppingCart.DoesNotExist:
            raise serializers.ValidationError('Рецепт не найден в списке покупок', status=status.HTTP_404_NOT_FOUND)

        shopping_cart_recipe.delete()


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер Ингредиент"""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериалайзер Рецепт Получить"""
    # забракованный серик, на удаление вероятнее всего
    class Meta:
        model = Recipe
        # поднастроить при тестировании через постман, если понадобится
        fields = '__all__'


class IngredientM2MSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(), source='ingredient')
    # здесь я беру поле ingredient и вытаскиваю из связанной модели нужное мне поле в нем 
    measurement_unit = serializers.StringRelatedField(read_only=True, source='ingredient.measurement_unit')
    name = serializers.StringRelatedField(read_only=True, source='ingredient.name')

    class Meta:
    
        model = IngredientRecipeAmount
        fields = ('id', 'amount', 'measurement_unit', 'name')
        read_only_fields = ('ingredient',)


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
        read_only_fields = ('name', 'color', 'slug')
    
    def to_internal_value(self, data):
        """Достает id из списка запроса и передает в поле id как значение словаря"""
        data_dict = {}
        for i in data:
            i = int(i)
            data_dict['id'] = i
        return data_dict['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер Рецепт"""
    ingredients = IngredientM2MSerializer(many=True, source='ingredient_used')
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)

    class Meta:

        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text', 'cooking_time', 'author', 'is_favorited', 'is_in_shopping_cart')
        # серик не ждет от пост запроса это поле, а сам подставит при создании
        read_only_fields = ('author', 'is_favorited', 'is_in_shopping_cart')

    
    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        is_in_shopping_cart = ShoppingCart.objects.filter(user=user, shopping_recipe=obj).exists()
        return is_in_shopping_cart

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        is_favorited = FavoriteRecipe.objects.filter(user=user, recipe=obj).exists()
        return is_favorited

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredient_used')
        tags_data = validated_data.pop('tags')
        author = self.context['request'].user
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags_data)
        for ingredient in ingredients:
            current_ingredient = ingredient.get('ingredient')
            amount = ingredient.get('amount')
            recipe.ingredients.add(
                current_ingredient,
                through_defaults={
                    'amount': amount
                }
            )
        return recipe
    # НУЖНО ПЕРЕПИСАТЬ АПДЕЙТ!!!!!
    # def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients_used')
        tags_data = validated_data.pop('tags')
        # обновляем рецепт полученными данными
        for attr, value  in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        # создаем или берем ингредиент
        for ingredient in ingredients:
            current_ingredient = ingredient.get
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
    author = UserRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('author',)
    
    def get_recipes_count(self, obj):
        user = self.context['request'].user
        recipes_count = Recipe.objects.filter(author=user).count()
        return recipes_count


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор Избранные рецепты"""
    # id = serializers.RecipeUserSerializer(source='recipe')

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
    # Нужен ли вообще метод делит, возможно хватит дэфолтного
    def delete(self, validated_data):
        id = validated_data.get('id')
        user = self.context['request'].user

        try:
            favorite_recipe = FavoriteRecipe.objects.get(recipe=id, user=user)
        except FavoriteRecipe.DoesNotExist:
            raise serializers.ValidationError('Рецепт не найден в избранном', status=status.HTTP_404_NOT_FOUND)

        favorite_recipe.delete()