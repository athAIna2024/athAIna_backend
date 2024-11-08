from rest_framework import serializers
from urllib3 import request
from accountapp.models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import smart_str, smart_bytes, force_str
from django.urls import reverse
from .utils import send_normal_email


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=69,min_length=8,write_only=True)
    password2 = serializers.CharField(max_length=69, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password2']

    def validate(self, attrs):
        password = attrs.get('password', '')
        password2 = attrs.get('password2', '')
        if password != password2:
            raise serializers.ValidationError('Password do not match')
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email = validated_data['email'],
            password=validated_data['password'],
        )
        return user

class VerifyUserEmailSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)