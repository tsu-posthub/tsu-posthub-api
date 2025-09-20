from rest_framework import serializers

class RegisterResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

class RefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
