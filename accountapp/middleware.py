from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.http import JsonResponse
from datetime import datetime, timezone
import jwt

class TokenFromCookieMiddleware(MiddlewareMixin):
    def process_request(self, request):
        access_token = request.COOKIES.get('access_token')

        if access_token:
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'


class TokenExpiryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                decoded_token = AccessToken(token)
                user_id = decoded_token['user_id']
                exp_timestamp = decoded_token['exp']
                current_timestamp = datetime.timestamp(datetime.now())

                # Update last activity timestamp in User model
                # This is a bit heavier than using cache, but works without cache
                from django.contrib.auth import get_user_model
                User = get_user_model()
                User.objects.filter(id=user_id).update(last_activity=timezone.now())

                # Check if token is about to expire (less than 5 minutes remaining)
                if exp_timestamp - current_timestamp < 300:
                    return JsonResponse({
                        'code': 'token_about_to_expire',
                        'message': 'Token is about to expire',
                        'successful': False
                    }, status=401)

            except (TokenError, jwt.ExpiredSignatureError):
                return JsonResponse({
                    'code': 'token_expired',
                    'message': 'Token has expired',
                    'successful': False
                }, status=401)
            except Exception:
                pass

        response = self.get_response(request)
        return response


class InactiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                # Decode the token to get the user ID
                decoded_token = AccessToken(token)
                user_id = decoded_token['user_id']

                # Check if the user is inactive
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    user = User.objects.get(id=user_id)
                    if user.status == user.INACTIVE:
                        return JsonResponse({
                            'detail': 'This account has been deactivated',
                            'successful': False
                        }, status=401)
                except User.DoesNotExist:
                    pass

            except (TokenError, jwt.ExpiredSignatureError):
                # Let TokenExpiryMiddleware handle expired tokens
                pass
            except Exception:
                pass

        return self.get_response(request)