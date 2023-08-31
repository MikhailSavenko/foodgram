import re

from rest_framework import serializers


def validate(self, data):
    """Валидация username в API"""
    username = data.get('username')
    if username and not re.match(r'^[\w.@+-]+$', username):
        raise serializers.ValidationError(
            'Поле username не соответствует паттерну',
        )
    if data.get('username') == 'me':
        raise serializers.ValidationError('Использовать имя me запрещено')
    return data