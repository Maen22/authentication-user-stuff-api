from django.contrib.auth import password_validation
from django.forms import ModelForm, CharField, ValidationError, ImageField
from validate_email import validate_email
from django.utils.translation import gettext_lazy as _

from . import serializers


class UserCreateForm(ModelForm):
    image = ImageField(required=False)
    confirm_password = CharField(max_length=128, required=True, empty_value=False)

    class Meta(serializers.CreateUserSerializer.Meta):
        pass

    # def save(self):

    def clean(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        email = self.cleaned_data['email']

        validate_email(email, verify=True)

        password_validation.validate_password(password=password)

        if password != confirm_password:
            raise ValidationError(_("Passwords doesn't match, Try again"))
