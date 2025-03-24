# accountapp/models.py

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _

from accountapp.managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    UNVERIFIED = 'unverified'
    VERIFIED = 'verified'
    INACTIVE = 'inactive'
    STATUS_CHOICES = [
        (UNVERIFIED, _('unverified')),
        (VERIFIED, _('verified')),
        (INACTIVE, _('inactive')),
    ]
    email = models.EmailField(max_length=255, unique=True, verbose_name=_('email_address'))
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=UNVERIFIED)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    archive_date = models.DateTimeField(auto_now=False, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    @property
    def __str__(self):
        return self.email

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    class meta:
        db_table = 'users'

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin')
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email

    class Meta:
        db_table = 'admins'

class Learner(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email

    class Meta:
        db_table = 'learners'

class OneTimePassword(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True)

    def __str__(self):
        return f"{self.user.email} - {self.code}"

    class Meta:
        db_table = 'OTP'