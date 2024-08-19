from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = verbose_name
        ordering = ('-id',)

    def __str__(self):
        return self.username

