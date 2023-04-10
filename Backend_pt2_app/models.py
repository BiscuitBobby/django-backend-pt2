from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models


class ManageUser(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        user = self.model(email=self.normalize_email(email)**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_su(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    username_field = 'email'

    # related_name argument
    groups = models.ManyToManyField(Group, blank=True, related_name='user_groups')
    user_permissions = models.ManyToManyField(Permission, blank=True, related_name='user_permissions')

    objects = ManageUser()

    def __str__(self):
        return self.email
