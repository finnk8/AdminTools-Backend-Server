from rest_framework import serializers
from .models import Teacher, Student, Class, Settings, Mother, Father

class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = '__all__'

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'

class MinimalClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['id']

class StudentSerializer(serializers.ModelSerializer):
    classes = MinimalClassSerializer(many=True, read_only=True)
    class Meta:
        model = Student
        fields = '__all__'

class MotherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mother
        fields = '__all__'

class FatherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Father
        fields = '__all__'