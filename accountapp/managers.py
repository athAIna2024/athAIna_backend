# accountapp/managers.py

from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError(_('Please enter a valid email address'))

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('Please enter an email address'))
        email = self.normalize_email(email)
        self.email_validator(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        from accountapp.models import Admin  # Local import to avoid circular import
        Admin.objects.create(user=user, is_staff=True, is_superuser=True, is_verified=True)
        return user