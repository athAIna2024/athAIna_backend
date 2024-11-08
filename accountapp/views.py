from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from accountapp.models import OneTimePassword
from accountapp.serializers import UserRegistrationSerializer, VerifyUserEmailSerializer, LoginSerializer
from accountapp.utils import send_code_to_user
from rest_framework.response import Response


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