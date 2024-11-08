from django.urls import path
from . import views
from .views import RegisterView, VerifyUserEmail, LoginUserView, TestAuthView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyUserEmail.as_view(), name='verify-email'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('profile-debug/', TestAuthView.as_view(), name='granted'),
]