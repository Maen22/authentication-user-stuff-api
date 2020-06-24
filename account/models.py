from django.db import models
from django.contrib.auth.models import BaseUserManager, \
    PermissionsMixin, AbstractUser
from django.utils.translation import gettext_lazy as _


class MyAccountManager(BaseUserManager):

    def create_user(self, email, first_name, last_name, gender, password=None, image=None):
        # Creates and save a new user

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            image=image,
        )
        user.set_password(password)
        user.is_active = False
        user.save()
        return user

    def create_superuser(self, email, first_name, last_name, gender, password, image=None):
        # Creates and save a new superUser

        user = self.create_user(
            email,
            first_name,
            last_name,
            gender,
            image,
            password
        )

        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class User(AbstractUser):
    # Choices for the gender field.
    male = 'M'
    female = 'F'
    GENDER_CHOICES = [(male, 'Male'), (female, 'Female')]

    username = None
    email = models.EmailField(verbose_name='email', max_length=255, unique=True, null=False)
    password = models.CharField(_('password'), max_length=128, null=False)
    first_name = models.CharField(max_length=50, null=False)
    last_name = models.CharField(max_length=50, null=False)
    image = models.ImageField(upload_to='uploads/', null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password', 'first_name', 'last_name', 'gender']

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_staff and self.is_superuser

    def has_module_perms(self, app_label):
        return True
