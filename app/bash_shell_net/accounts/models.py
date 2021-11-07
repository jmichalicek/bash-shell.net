from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'email'

    email = models.EmailField(_('Email address'), unique=True, db_index=True)
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

    def __str__(self):
        return self.email

    def get_short_name(self):
        return self.first_name

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email

        super().save(*args, **kwargs)
