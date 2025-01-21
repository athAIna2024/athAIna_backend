from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils import timezone

from django.shortcuts import render
from google.protobuf.proto_json import serialize
from rest_framework.generics import GenericAPIView, UpdateAPIView, DestroyAPIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from accountapp.models import OneTimePassword, User, Learner
from accountapp.serializers import UserRegistrationSerializer, VerifyUserEmailSerializer, LoginSerializer, \
    SetNewPasswordSerializer, \
    PasswordResetRequestSerializer, LogoutUserSerializer, ChangePasswordSerializer, ChangePasswordRequestSerializer
from accountapp.utils import send_code_to_user
from rest_framework.response import Response
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError, smart_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator


# Create your views here.

class RegisterView(GenericAPIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        user_data = request.data
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            Learner.objects.create(user=user)
            send_code_to_user(user.email)
            serializer_data = serializer.data
            return Response({
                "data": serializer_data,
                "message": "User created successfully",
                "successful": True
            }, status=status.HTTP_201_CREATED)
        return Response({serializer.errors,}, status=status.HTTP_400_BAD_REQUEST)

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
            if user.status == user.UNVERIFIED:
                user.status = user.VERIFIED
                user.save()
                user_code_obj.delete()
                return Response({
                    "message": "Email verified successfully",
                    "successful": True
                }, status=status.HTTP_200_OK)
            return Response({
                "message": "Email already verified",
                "successful": False
            }, status=status.HTTP_200_OK)
        except OneTimePassword.DoesNotExist:
            return Response({
                "message": "Invalid OTP",
                "successful": False
            }, status=status.HTTP_400_BAD_REQUEST)
class LoginUserView(GenericAPIView):
    serializer_class = LoginSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        response = Response(serializer.data, status=status.HTTP_200_OK)
        access_token = serializer.data.get('access_token')
        refresh_token = serializer.data.get('refresh_token')
        response.set_cookie('access_token', access_token, httponly=True, max_age=3600)  # 1 hour
        response.set_cookie('refresh_token', refresh_token, httponly=True, max_age=1209600)  # 30 days
        return Response(serializer.data, status=status.HTTP_200_OK)

# class TestAuthView(GenericAPIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         data = {
#             "message": "debug - authentication feature working"
#         }
#         return Response(data, status=status.HTTP_200_OK)
# class PasswordResetRequestView(GenericAPIView):
#     serializer_class=PasswordResetRequestSerializer
#     def post(self, request):
#         serializer = self.serializer_class(data=request.data,context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         return Response({
#             "message": "A link has been sent to your email to reset your password"
#         }, status=status.HTTP_200_OK)

# class PasswordResetConfirm(GenericAPIView):
#     serializer_class = SetNewPasswordSerializer
#
#     def post(self, request, uidb64, token):
#         otp_code = request.data.get('otp')
#         try:
#             user_id = smart_str(urlsafe_base64_decode(uidb64))
#             user = User.objects.get(id=user_id)
#             if not PasswordResetTokenGenerator().check_token(user, token):
#                 return Response({
#                     "msg": "Token is not valid, please request a new one"
#                 }, status=status.HTTP_401_UNAUTHORIZED)
#             otp_obj = OneTimePassword.objects.get(code=otp_code)
#             if otp_obj.user != user:
#                 return Response({
#                     "msg": "Invalid OTP"
#                 }, status=status.HTTP_400_BAD_REQUEST)
#             otp_obj.delete()  # Delete the OTP after successful verification
#             return Response({
#                 "success": True,
#                 "msg": "Credentials Valid",
#                 "uidb64": uidb64,
#                 "token": token,
#                 "otp": otp_code
#             }, status=status.HTTP_200_OK)
#         except (OneTimePassword.DoesNotExist, DjangoUnicodeDecodeError, User.DoesNotExist):
#             return Response({
#                 "msg": "Invalid OTP or token"
#             }, status=status.HTTP_400_BAD_REQUEST)

class SetNewPassword(GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request, uidb64, token):
        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({
                    "message": "Token is not valid, please request a new one",
                    "successful": False
                }, status=status.HTTP_401_UNAUTHORIZED)
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response({
                "message": "Password reset successful",
                "successful": True
            }, status=status.HTTP_200_OK)
        except (DjangoUnicodeDecodeError, User.DoesNotExist):
            return Response({
                "message": "Invalid token",
                "successful": False
            }, status=status.HTTP_400_BAD_REQUEST)



class SetChangePassword(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, uidb64, token):
        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({
                    "message": "Token is not valid, please request a new one",
                    "successful": False
                }, status=status.HTTP_401_UNAUTHORIZED)
            serializer = self.serializer_class(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({
                "message": "Password updated successfully",
                "successful": True
            }, status=status.HTTP_200_OK)
        except (DjangoUnicodeDecodeError, User.DoesNotExist):
            return Response({
                "message": "Invalid token",
                "successful": False
            }, status=status.HTTP_400_BAD_REQUEST)

class OTPVerificationView(GenericAPIView):
    serializer_class = VerifyUserEmailSerializer

    def post(self, request):
        otp_code = request.data.get('otp')
        try:
            otp_obj = OneTimePassword.objects.get(code=otp_code)
            user = otp_obj.user
            refresh = RefreshToken.for_user(user)
            otp_obj.delete()  # Delete the OTP after successful verification
            response = Response({
                "successful": True,
                "msg": "OTP is valid",
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)
            response.set_cookie('access_token', str(refresh.access_token), httponly=True)
            response.set_cookie('refresh_token', str(refresh), httponly=True)
            return response
        except OneTimePassword.DoesNotExist:
            return Response({
                "msg": "Invalid or expired OTP",
                "successful": False
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
            "message": "Password reset successful",
            "successful": True
        }, status=status.HTTP_200_OK)

class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password updated successfully",
                         "successful":True}, status=status.HTTP_200_OK)

class LogoutUserView(GenericAPIView):
    serializer_class = LogoutUserSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            response = Response(status=status.HTTP_204_NO_CONTENT)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            return response
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class DeleteUserView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.status = user.INACTIVE
        user.archive_date = timezone.now()
        user.save()
        return Response({
            "message": "User deleted successfully",
            "successful": True
        }, status=status.HTTP_200_OK)


class PasswordChangeRequestView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response({
            "message": "An OTP has been sent to your email to verify your identity",
            "successful": True
        }, status=status.HTTP_200_OK)

class ChangePasswordRequestView(GenericAPIView):
    serializer_class = ChangePasswordRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response({
            "message": "An OTP has been sent to your email to verify your identity",
            "successful": True
        }, status=status.HTTP_200_OK)
# change password
class VerifyPasswordChangeOTPView(GenericAPIView):
    serializer_class = VerifyUserEmailSerializer

    def post(self, request):
        otp_code = request.data.get('otp')
        try:
            otp_obj = OneTimePassword.objects.get(code=otp_code)
            user = otp_obj.user
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request).domain
            relative_link = reverse('set-new-password', kwargs={'uidb64': uidb64, 'token': token})
            abslink = f"http://{current_site}{relative_link}"
            otp_obj.delete()  # Delete the OTP after successful verification
            return Response({
                "message": "OTP verified successfully",
                "successful": True,
                "password_reset_link": abslink
            }, status=status.HTTP_200_OK)
        except OneTimePassword.DoesNotExist:
            return Response({
                "message": "Invalid or expired OTP",
                "successful": False

            }, status=status.HTTP_400_BAD_REQUEST)

#forget password
class VerifyChangePasswordOTPView(GenericAPIView):
    serializer_class = VerifyUserEmailSerializer

    def post(self, request):
        otp_code = request.data.get('otp')
        try:
            otp_obj = OneTimePassword.objects.get(code=otp_code)
            user = otp_obj.user
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request).domain
            relative_link = reverse('set-change-password', kwargs={'uidb64': uidb64, 'token': token})
            abslink = f"http://{current_site}{relative_link}"
            otp_obj.delete()  # Delete the OTP after successful verification
            return Response({
                "message": "OTP verified successfully",
                "successful": True,
                "password_reset_link": abslink
            }, status=status.HTTP_200_OK)
        except OneTimePassword.DoesNotExist:
            return Response({
                "message": "Invalid or expired OTP",
                "successful": False
            }, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            try:
                old_refresh_token = request.data.get('refresh')
                if old_refresh_token:
                    old_token = RefreshToken(old_refresh_token)
                    old_token.blacklist()
                response.data['message'] = 'Token refreshed successfully'
            except Exception as e:
                return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        return response