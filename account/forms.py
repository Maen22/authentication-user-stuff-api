from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, CharField, ValidationError, ImageField
from validate_email import validate_email
from django.utils.translation import gettext_lazy as _

from . import serializers
from .models import User


class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'gender']

    # def save(self):

    # def clean(self):
    #     password = self.cleaned_data['password']
    #     confirm_password = self.cleaned_data['confirm_password']
    #     email = self.cleaned_data['email']
    #
    #     validate_email(email, verify=True)
    #
    #     password_validation.validate_password(password=password)
    #
    #     if password != confirm_password:
    #         raise ValidationError(_("Passwords doesn't match, Try again"))
