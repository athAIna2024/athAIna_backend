from django.shortcuts import render
from google.protobuf.proto_json import serialize
from rest_framework.generics import GenericAPIView, UpdateAPIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from accountapp.models import OneTimePassword, User
from accountapp.serializers import UserRegistrationSerializer, VerifyUserEmailSerializer, LoginSerializer, \
    SetNewPasswordSerializer, \
    PasswordResetRequestSerializer, LogoutUserSerialezer, ChangePasswordSerializer
from accountapp.utils import send_code_to_user
from rest_framework.response import Response
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator


# Create your views here.

class RegisterView(GenericAPIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        user_data = request.data
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user=serializer.data
            send_code_to_user(user_data['email'])
            return Response({
                "data": user,
                "message": "User created successfully",
            },status=status.HTTP_201_CREATED)
        return Response({serializer.errors},status=status.HTTP_400_BAD_REQUEST)

class VerifyUserEmail(GenericAPIView):
    serializer_class = VerifyUserEmailSerializer

    def post(self, request):
        otpCode = None
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            otpCode = serializer.validated_data.get('otp')

        try:
            user_code_obj = OneTimePassword.objects.get(code=otpCode)
            user = user_code_obj.user
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response({
                    "message": "Email verified successfully"
                }, status=status.HTTP_200_OK)
            return Response({
                "message": "Email already verified"
            }, status=status.HTTP_200_OK)
        except OneTimePassword.DoesNotExist:
            return Response({
                "message": "Invalid OTP"
            }, status=status.HTTP_400_BAD_REQUEST)

class LoginUserView(GenericAPIView):
    serializer_class = LoginSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TestAuthView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = {
            "message": "debug - authentication feature working"
        }
        return Response(data, status=status.HTTP_200_OK)
class PasswordResetRequestView(GenericAPIView):
    serializer_class=PasswordResetRequestSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data,context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response({
            "message": "A link has been sent to your email to reset your password"
        }, status=status.HTTP_200_OK)

class PasswordResetConfirm(GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def post(self, request, uidb64, token):
        otp_code = request.data.get('otp')
        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({
                    "msg": "Token is not valid, please request a new one"
                }, status=status.HTTP_401_UNAUTHORIZED)
            otp_obj = OneTimePassword.objects.get(code=otp_code)
            if otp_obj.user != user:
                return Response({
                    "msg": "Invalid OTP"
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                "success": True,
                "msg": "Credentials Valid",
                "uidb64": uidb64,
                "token": token,
                "otp": otp_code
            }, status=status.HTTP_200_OK)
        except (OneTimePassword.DoesNotExist, DjangoUnicodeDecodeError, User.DoesNotExist):
            return Response({
                "msg": "Invalid OTP or token"
            }, status=status.HTTP_400_BAD_REQUEST)
class SetNewPassword(GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({
            "message": "Password reset successful"
        }, status=status.HTTP_200_OK)


class OTPVerificationView(GenericAPIView):
    serializer_class = VerifyUserEmailSerializer

    def post(self, request):
        otp_code = request.data.get('otp')
        try:
            otp_obj = OneTimePassword.objects.get(code=otp_code)
            user = otp_obj.user
            refresh = RefreshToken.for_user(user)
            return Response({
                "success": True,
                "msg": "OTP is valid",
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        except OneTimePassword.DoesNotExist:
            return Response({
                "msg": "Invalid OTP"
            }, status=status.HTTP_400_BAD_REQUEST)

class PasswordChangeView(GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['password'])
        user.save()
        return Response({
            "message": "Password reset successful"
        }, status=status.HTTP_200_OK)

class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)

class LogoutUserView(GenericAPIView):
    serializer_class=LogoutUserSerialezer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)