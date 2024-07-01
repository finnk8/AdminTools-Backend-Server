# serializers.py
from djoser.serializers import UserSerializer
from django.contrib.auth import get_user_model

class CustomCurrentUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = get_user_model()
        fields = ('id', 'username', 'email', 'first_name', 'last_name')