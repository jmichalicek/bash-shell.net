from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields) -> 'User':
        """
        Creates and saves a User with the given username, email, and password.
        """

        if not email:
            raise ValueError('The given email must be set')

        email = UserManager.normalize_email(email)
        user: User = User(email=email, is_active=True, is_staff=False, is_superuser=False, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields) -> 'User':
        """
        Creates and saves a staff superuser
        """

        u = self.create_user(email, password, **extra_fields)
        # Could just pass these as extra_fields to create_user()
        # but this is more explicit and allows create_user to ensure
        # that the correct settings are enforced for a normal user.
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u


class User(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'email'
    # USERNAME_FIELD = "username"

    email = models.EmailField(_('Email address'), unique=True, db_collation="case_insensitive")
    first_name = models.CharField(_('First Name'), max_length=50, blank=True)
    last_name = models.CharField(_('Last Name'), max_length=50, blank=True)
    is_staff = models.BooleanField(
        _('staff status'), default=False, help_text=_('Designates whether the user can log into this admin ' 'site.')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as ' 'active. Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('Date Joined'), default=timezone.now)
    username = models.CharField(
        max_length=50,
        blank=True,
        unique=True,
        db_index=True,
        help_text=_('Username to alternately display instead of email address'),
    )

    objects = UserManager()

    def __str__(self) -> str:
        return self.email

    def get_short_name(self) -> str:
        return self.first_name

    def get_full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'

    def save(self, *args, **kwargs) -> None:
        if not self.username:
            self.username = self.email

        super().save(*args, **kwargs)
