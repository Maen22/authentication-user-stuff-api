from django.db import models
from django.contrib.auth.models import BaseUserManager, \
    PermissionsMixin, AbstractUser
from django.utils.translation import gettext_lazy as _
from organization.models import Organization


class MyAccountManager(BaseUserManager):

    def create_user(self, email, first_name, last_name, gender, organization, image=None, password=None,):
        # Creates and save a new user

        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            image=image,
            organization=Organization.objects.get(name=organization)
        )
        user.set_password(password)
        user.is_active = False
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, gender, organization, image=None, password=None):
        # Creates and save a new superUser

        user = self.create_user(
            email,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            image=image,
            organization=organization,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    # Choices for the gender field.
    male = 'M'
    female = 'F'
    GENDER_CHOICES = [(male, 'Male'), (female, 'Female')]

    username = None
    email = models.EmailField(verbose_name='email', max_length=255, unique=True, null=False)
    first_name = models.CharField(max_length=50, null=False)
    last_name = models.CharField(max_length=50, null=False)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=False)
    image = models.ImageField(upload_to='uploads/', null=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='users', default='No Org', db_constraint=False)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'gender']

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        # Simplest possible answer: All admins are staff
        return self.is_admin
