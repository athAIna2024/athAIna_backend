from django.urls import path
from . import views
from .views import RegisterView, VerifyUserEmail

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyUserEmail.as_view(), name='verify-email'),
]