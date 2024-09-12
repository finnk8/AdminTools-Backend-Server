from rest_framework import serializers
from django.contrib.auth.models import User
from profiles.models import UserProfile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['iserv_domain']  # Add more fields as needed

class CustomUserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()  # Allow profile updates

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'profile']

    def to_representation(self, instance):
        # Get the standard representation
        representation = super().to_representation(instance)
        
        # Check if the user has a profile; if not, return an empty profile or handle it as needed
        if not hasattr(instance, 'profile'):
            UserProfile.objects.create(user=instance).save()
            representation['profile'] = ProfileSerializer(instance.profile).data
        
        return representation
    
    def update(self, instance, validated_data):
        # Pop the profile data from the validated data
        profile_data = validated_data.pop('profile', None)

        # Update the User fields (username, email, etc.)
        instance = super().update(instance, validated_data)

        # Update the profile if the data is provided
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance