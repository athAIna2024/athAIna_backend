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
    email = serializers.EmailField(
        max_length=255,
        error_messages={
            'unique': 'user with this email address already exists.'
        }
    )
    class Meta:
        model = User
        fields = ['email', 'password', 'password2']
        # Add this to explicitly set validators for email field
        extra_kwargs = {
            'email': {'validators': []}  # Remove default validators
        }

    def validate_email(self, value):
        # This runs before the validate method
        if User.objects.filter(email=value).exists():
            user = User.objects.get(email=value)
            if user.status == 'inactive':
                raise serializers.ValidationError('This account has been deactivated. Please contact us')
            else:
                raise serializers.ValidationError('user with this email address already exists.')
        return value

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

        # Collect all password validation errors
        requirements_failed = []

        if len(password) < 8:
            requirements_failed.append("at least 8 characters long")

        if password.isdigit():
            requirements_failed.append("not be entirely numeric")

        if not re.search(r'\d', password):
            requirements_failed.append("contain at least one number")

        if not re.search(r'[A-Z]', password):
            requirements_failed.append("contain at least one uppercase letter")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            requirements_failed.append("contain at least one special character")

        # If any requirements failed, raise a single error with all requirements
        if requirements_failed:
            error_message = "Password must: " + ", ".join(requirements_failed)
            raise serializers.ValidationError(error_message)

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

    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError('Invalid email address format')

        try:
            user = User.objects.get(email=value)
            if user.status == 'inactive':
                raise serializers.ValidationError('This account has been deactivated. Please contact us.')
        except User.DoesNotExist:
            raise serializers.ValidationError('No user found with this email address')

        return value

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        request = self.context.get('request')

        user = authenticate(request, email=email, password=password)
        if not user:
            raise serializers.ValidationError({'password': 'Incorrect password'})

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
            email_body = f"Hello {user.email},\n\nYour One Time Password for Change Password is {otp_code.code}\n\nRegards,\nathAIna Team"
            data = {
                'email_body': email_body,
                'email_subject': f"Change Password: {otp_code.code}",
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
            email_body = f"Hello {user.email},\n\nYour One Time Password for Forgot Password is {otp_code.code}\n\nRegards,\nathAIna Team"
            data = {
                'email_body': email_body,
                'email_subject': f"Forgot Password: {otp_code.code}",
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

        # Collect all password validation errors
        requirements_failed = []

        if len(password) < 8:
            requirements_failed.append("at least 8 characters long")

        if password.isdigit():
            requirements_failed.append("not be entirely numeric")

        if not re.search(r'\d', password):
            requirements_failed.append("contain at least one number")

        if not re.search(r'[A-Z]', password):
            requirements_failed.append("contain at least one uppercase letter")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            requirements_failed.append("contain at least one special character")

        # If any requirements failed, raise a single error with all requirements
        if requirements_failed:
            error_message = "Password must: " + ", ".join(requirements_failed)
            raise serializers.ValidationError(error_message)

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

        # Collect all password validation errors
        requirements_failed = []

        if len(new_password) < 8:
            requirements_failed.append("at least 8 characters long")

        if new_password.isdigit():
            requirements_failed.append("not be entirely numeric")

        if not re.search(r'\d', new_password):
            requirements_failed.append("contain at least one number")

        if not re.search(r'[A-Z]', new_password):
            requirements_failed.append("contain at least one uppercase letter")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
            requirements_failed.append("contain at least one special character")

        # If any requirements failed, raise a single error with all requirements
        if requirements_failed:
            error_message = "Password must: " + ", ".join(requirements_failed)
            raise serializers.ValidationError(error_message)

        if not user.check_password(old_password):
            raise serializers.ValidationError('Old password did not match our records')

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


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    purpose = serializers.ChoiceField(
        choices=['signup', 'change_password', 'forgot_password'],
        required=True
    )

    class Meta:
        fields = ['email', 'purpose']

    def validate(self, attrs):
        email = attrs.get('email')
        purpose = attrs.get('purpose')

        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('No user found with this email address')

        user = User.objects.get(email=email)

        # Delete any existing OTP for the user
        OneTimePassword.objects.filter(user=user).delete()

        # Create new OTP
        otp_code = OneTimePassword.objects.create(user=user, code=generateOtp())

        # Prepare email based on purpose
        if purpose == 'signup':
            subject = f"One Time Password for Email Verification"
            email_body = f"Hello {user.email},\n\nYour One Time Password for Email Verification is {otp_code.code}\n\nRegards,\nathAIna Team"
        elif purpose == 'change_password' :
            subject = f"Change Password: {otp_code.code}"
            email_body = f"Hello {user.email},\n\nYour One Time Password for Change Password is {otp_code.code}\n\nRegards,\nathAIna Team"
        else:  # forgot_password
            subject = f"Forgot Password: {otp_code.code}"
            email_body = f"Hello {user.email},\n\nYour One Time Password for Forgot Password is {otp_code.code}\n\nRegards,\nathAIna Team"


# email_body = f"Your OTP code is {otp_code.code}"
        data = {
            'email_body': email_body,
            'email_subject': subject,
            'to_email': user.email
        }
        send_normal_email(data)

        return attrs