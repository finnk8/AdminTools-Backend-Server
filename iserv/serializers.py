from rest_framework import serializers
from .models import IservGroup, ExistingAccount

class IservGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = IservGroup
        fields = '__all__'

class ExistingAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExistingAccount
        fields = '__all__'