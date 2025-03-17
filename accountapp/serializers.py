from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from httplib2.auth import token
from rest_framework import serializers
from urllib3 import request
from accountapp.models import User, OneTimePassword
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import smart_str, smart_bytes, force_str
from django.urls import reverse
from .utils import send_normal_email, generateOtp
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import smart_str, smart_bytes, force_str
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken,TokenError
import re

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=69, min_length=8, write_only=True)
    password2 = serializers.CharField(max_length=69, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password2']

    def validate(self, attrs):
        password = attrs.get('password', '')
        password2 = attrs.get('password2', '')
        email = attrs.get('email', '')

        try:
            validate_email(email)
        except ValidationError:
            raise serializers.ValidationError('Invalid email address format')

        if password != password2:
            raise serializers.ValidationError('Passwords do not match')

        if len(password) < 8:
            raise serializers.ValidationError('Password must be longer than 8 characters')

        if password.isdigit():
            raise serializers.ValidationError('Password cannot be completely numeric')

        if not re.search(r'\d', password):
            raise serializers.ValidationError('Password must contain at least one number')

        if not re.search(r'[A-Z]', password):
            raise serializers.ValidationError('Password must contain at least one uppercase letter')

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise serializers.ValidationError('Password must contain at least one special character')




        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user

class VerifyUserEmailSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=6)
    password = serializers.CharField(max_length=69, min_length=8, write_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'access_token', 'refresh_token']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        request = self.context.get('request')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('No user found with this email address')

        user = authenticate(request, email=email, password=password)
        if not user:
            raise serializers.ValidationError('Incorrect password')

        if user.status != 'verified':
            raise AuthenticationFailed('Account is not verified')

        user_tokens = user.token()

        return {
            'email': user.email,
            'password': password,
            'access_token': str(user_tokens.get('access')),
            'refresh_token': str(user_tokens.get('refresh')),
        }

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            # Delete any existing OTP for the user
            OneTimePassword.objects.filter(user=user).delete()
            otp_code = OneTimePassword.objects.create(user=user, code=generateOtp())  # Assuming generate_otp() is a utility function to generate OTP
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            request = self.context.get('request')
            email_body = f"Your OTP code is {otp_code.code}"
            data = {
                'email_body': email_body,
                'email_subject': "Change your Password",
                'to_email': user.email
            }
            send_normal_email(data)
        return super().validate(attrs)
class ChangePasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            # Delete any existing OTP for the user
            OneTimePassword.objects.filter(user=user).delete()
            otp_code = OneTimePassword.objects.create(user=user, code=generateOtp())  # Assuming generate_otp() is a utility function to generate OTP
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            request = self.context.get('request')
            email_body = f"Your OTP code is {otp_code.code}"
            data = {
                'email_body': email_body,
                'email_subject': "Reset your Password",
                'to_email': user.email
            }
            send_normal_email(data)
        return super().validate(attrs)

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    confirm_password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    class Meta:
        fields = ['password', 'confirm_password']

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError('Passwords do not match')

        if len(password) < 8:
            raise serializers.ValidationError('Password must be longer than 8 characters')
        if password.isdigit():
            raise serializers.ValidationError('Password cannot be entirely numeric')

        if not re.search(r'\d', password):
            raise serializers.ValidationError('Password must contain at least one number')

        if not re.search(r'[A-Z]', password):
            raise serializers.ValidationError('Password must contain at least one uppercase letter')

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise serializers.ValidationError('Password must contain at least one special character')



        return attrs

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=100, min_length=8, write_only=True)
    new_password = serializers.CharField(max_length=100, min_length=8, write_only=True)
    confirm_new_password = serializers.CharField(max_length=100, min_length=8, write_only=True)

    class Meta:
        fields = ['old_password', 'new_password', 'confirm_new_password']

    def validate(self, attrs):
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_new_password = attrs.get('confirm_new_password')
        user = self.context['request'].user

        if new_password != confirm_new_password:
            raise serializers.ValidationError('New passwords do not match')

        if new_password == old_password:
            raise serializers.ValidationError('New password cannot be the same as the old password')

        if len(new_password) < 8:
            raise serializers.ValidationError('Password must be longer than 8 characters')

        if new_password.isdigit():
            raise serializers.ValidationError('Password cannot be entirely numeric')

        if not re.search(r'\d', new_password):
            raise serializers.ValidationError('Password must contain at least one number')
        if not re.search(r'[A-Z]', new_password):
            raise serializers.ValidationError('Password must contain at least one uppercase letter')

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
            raise serializers.ValidationError('Password must contain at least one special character')

        if not user.check_password(old_password):
            raise serializers.ValidationError('Old password is incorrect')

        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class LogoutUserSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    default_error_messages = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token=attrs.get('refresh_token')
        return attrs

    def save(self, **kwargs):
        try:
            token=RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            return self.fail('bad_token')
