from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Deck, Flashcard

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class FlashcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flashcard
        fields = ['id', 'deck', 'question', 'answer', 'created_at']

# class DeckSerializer(serializers.ModelSerializer):
#     flashcards = FlashcardSerializer(many=True, read_only=True)

#     class Meta:
#         model = Deck
#         fields = ['id', 'title', 'flashcards']

class DeckSerializer(serializers.ModelSerializer):
    flashcards = FlashcardSerializer(many=True, read_only=True)

    class Meta:
        model = Deck
        fields = ['id', 'title', 'flashcards', 'user']
        read_only_fields = ['user']  # Ensure user field is read-only to avoid manipulation

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data.pop('user', None)  # Safely remove user if exists to avoid conflict
        return Deck.objects.create(**validated_data, user=user)