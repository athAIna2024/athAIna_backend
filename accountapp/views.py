from django.contrib.auth import authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.urls import reverse
from django.utils import timezone

from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect

from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from google.protobuf.proto_json import serialize
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import GenericAPIView, UpdateAPIView, DestroyAPIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from accountapp import serializers
from accountapp.models import OneTimePassword, User, Learner
from accountapp.serializers import UserRegistrationSerializer, VerifyUserEmailSerializer, LoginSerializer, \
    SetNewPasswordSerializer, \
    PasswordResetRequestSerializer, LogoutUserSerializer, ChangePasswordSerializer, ChangePasswordRequestSerializer, \
    ResendOTPSerializer
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

    def post(self, request, *args, **kwargs):
        # try:
            # Retrieve and blacklist the old refresh token
            old_refresh_token = request.COOKIES.get('refresh_token')
            if old_refresh_token:
                try:
                    old_token = RefreshToken(old_refresh_token)
                    old_token.blacklist()
                except TokenError:
                    pass  # Ignore if the token is already invalid or expired

            # Validate user credentials
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(email=email, password=password)

            if user is not None:
                # Generate new tokens
                refresh = RefreshToken.for_user(user)
                csrf = get_token(request)
                response = Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'message': 'Login successful',
                    'user_id': user.id,
                    'email': email,
                    'login_date': timezone.now(),
                    'user_date_joined': user.date_joined,
                    'successful': True
                }, status=status.HTTP_200_OK)

                # Set cookies for tokens
                response.set_cookie('access_token', str(refresh.access_token), httponly=False, samesite='None', secure=True, max_age=3600)
                response.set_cookie('refresh_token', str(refresh), httponly=False, samesite='None', secure=True, max_age=604800)
                response.set_cookie('athAIna_csrfToken', csrf, samesite='None', secure=True)
                return response
            else:
                return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # except Exception as e:
        #     return Response(str(e), status=status.HTTP_400_BAD_REQUEST)



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
                }, status=status.HTTP_400_BAD_REQUEST)
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
        except Exception as e:
            # Make sure to return the response with serializer errors
            # in the same format as other endpoints
            return Response({
                "message": serializer.errors,
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
                }, status=status.HTTP_400_BAD_REQUEST)
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
        except Exception as e:
            # Match the format used in SetNewPassword for consistency
            return Response({
                "message": serializer.errors,
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

    def post(self, request):
        try:
            # Retrieve tokens from cookies
            refresh_token = request.COOKIES.get('refresh_token')
            access_token = request.COOKIES.get('access_token')

            if not refresh_token or not access_token:
                return Response({
                    "error": "Tokens not found in cookies",
                    "successful": False
                }, status=status.HTTP_401_UNAUTHORIZED)

            # Validate the refresh token
            try:
                refresh_token_obj = RefreshToken(refresh_token)
                refresh_token_obj.blacklist()  # Blacklist the refresh token
            except TokenError:
                return Response({
                    "error": "Refresh token is expired or invalid",
                    "successful": False
                }, status=status.HTTP_401_UNAUTHORIZED)

            # Validate the access token
            try:
                access_token_obj = AccessToken(access_token)
                # Access tokens are validated upon creation
            except TokenError:
                return Response({
                    "error": "Access token is expired or invalid",
                    "successful": False
                }, status=status.HTTP_401_UNAUTHORIZED)

            # Delete cookies and return success response
            response = Response({
                "successful": True,
                "message": "User logged out successfully"
            }, status=status.HTTP_204_NO_CONTENT)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            response.delete_cookie('athAIna_csrfToken')
            return response

        except Exception as e:
            return Response({
                "error": f"An error occurred during logout: {str(e)}",
                "successful": False
            }, status=status.HTTP_400_BAD_REQUEST)

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
            relative_link = reverse('change-password', kwargs={'uidb64': uidb64, 'token': token})
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
            relative_link = reverse('forgot-password', kwargs={'uidb64': uidb64, 'token': token})
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
        try:
            # Retrieve the refresh token from the cookies
            refresh_token = request.COOKIES.get('refresh_token')

            if not refresh_token:
                return Response(
                    {"error": "No refresh token found in cookies", "successful": False},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Validate and blacklist the old refresh token
            try:
                old_token = RefreshToken(refresh_token)
                old_token.blacklist()  # Blacklist the old token
            except TokenError:
                return Response(
                    {"error": "Refresh token is expired or invalid", "successful": False},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Generate new tokens for the user
            user = User.objects.get(id=old_token.payload.get('user_id'))
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            csrf = get_token(request)

            # Set cookies for the new tokens
            response = Response({
                'access': access_token,
                'message': 'Token refreshed successfully',
                'successful': True
            }, status=status.HTTP_200_OK)
            response.set_cookie('access_token', access_token, httponly=False, samesite='None', secure=True, max_age=3600)
            response.set_cookie('refresh_token', str(refresh), httponly=False, samesite='None', secure=True, max_age=604800)
            response.set_cookie('athAIna_csrfToken', csrf, samesite='None', secure=True)

            return response

        except User.DoesNotExist:
            return Response(
                {"error": "User not found", "successful": False},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred while refreshing the token: {str(e)}", "successful": False},
                status=status.HTTP_400_BAD_REQUEST
            )

class CheckUserTokensView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Current tokens retrieved successfully',
            'successful': True
        }, status=status.HTTP_200_OK)


class ResendOTPView(GenericAPIView):
    serializer_class = ResendOTPSerializer
    authentication_classes = []  # No authentication required
    permission_classes = []  # No permissions required

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response({
            "successful": True,
            "message": "OTP has been resent to your email"
        }, status=status.HTTP_200_OK)