from django.urls import path
from . import views
from .views import RegisterView, VerifyUserEmail, LoginUserView, TestAuthView, PasswordResetConfirm, \
    PasswordResetRequestView, SetNewPassword, OTPVerificationView, PasswordChangeView, LogoutUserView, \
    ChangePasswordView, PasswordChangeRequestView, VerifyPasswordChangeOTPView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyUserEmail.as_view(), name='verify-email'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('profile-debug/', TestAuthView.as_view(), name='granted'),

    # path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    # path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name='reset-password-confirm'),
    # path('set-new-password/', SetNewPassword.as_view(), name='set-new-password'),
    path('otp-verify/', OTPVerificationView.as_view(), name='otp-verify'),
    path('password-change/', PasswordChangeView.as_view(), name='password-change'),

    path('logout/', LogoutUserView.as_view(), name='logout'),

    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('delete-account/', views.DeleteUserView.as_view(), name='delete-account'),
    path('password-change-request/', PasswordChangeRequestView.as_view(), name='password-change-request'),
    path('verify-password-change-otp/', VerifyPasswordChangeOTPView.as_view(), name='verify-password-change-otp'),
    path('set-new-password/<uidb64>/<token>/', SetNewPassword.as_view(), name='set-new-password'),

]