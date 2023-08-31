from rest_framework import serializers
from validators import validate

from backend.foodgram.users.models import Subscription, User


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписки"""
    # как сделать пост запрос с id User-a и подписаться на него
    author = serializers.PrimaryKeyRelatedField()
    
    class Meta:
        model = Subscription
        # через related_name пытаюсь достать подписки 
        fields = ('subscriber', 'author')


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
    
