from django.contrib.auth import get_user_model, authenticate, password_validation
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework import serializers
from validate_email import validate_email

from organization.models import Organization
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'gender', 'image']
        extra_kwargs = {'password': {'write_only': True}}


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta(UserSerializer.Meta):
        fields = ['id', 'email', 'first_name', 'last_name', 'gender']


class CreateUserSerializer(UserSerializer):
    confirm_password = serializers.CharField(max_length=128, allow_blank=False, required=True, write_only=True)

    class Meta(UserSerializer.Meta):
        fields = ['email', 'password', 'first_name', 'last_name', 'gender', 'image', 'confirm_password']

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        organization_name = validated_data.pop('organization_name')

        org = Organization.objects.get(name=organization_name)

        return User.objects.create_user(**validated_data, organization=org)

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        email = attrs.get('email')

        validate_email(email, verify=True)

        password_validation.validate_password(password=password)

        if password != confirm_password:
            raise serializers.ValidationError(_("Passwords doesn't match, Try again"))

        return attrs


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(label=_("email"))
    password = serializers.CharField(
        label=_("password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if user is None:
            msg = _('Unable to authenticate with provided credentials')
            raise exceptions.NotAuthenticated(msg)
        attrs['user'] = user
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, allow_blank=False, required=True)
    new_password = serializers.CharField(max_length=128, allow_blank=False, required=True)
    confirm_password = serializers.CharField(max_length=128, allow_blank=False, required=True)

    def validate(self, attrs):
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        user = self.context.get('request').user
        if not user.check_password(old_password):
            raise serializers.ValidationError(_("Old password doesn't match"))

        password_validation.validate_password(password=new_password, user=user)

        if not new_password == confirm_password:
            raise serializers.ValidationError(_("Passwords doesn't match"))

        attrs['user'] = user

        return attrs
