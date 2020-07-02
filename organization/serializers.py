from django.shortcuts import get_object_or_404
from rest_framework import serializers

from account.models import User
from account.serializers import UserSerializer
from .models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    owner = UserSerializer()

    # users = UserSerializer(many=True)

    class Meta:
        model = Organization
        fields = ['id', 'name', 'location', 'phone', 'owner']

    def create(self, validated_data):
        return Organization.objects.create(owner=self.context.get('request').user, **validated_data)


class AddingUsersSerializer(serializers.Serializer):
    pks = serializers.ListField(
        child=serializers.IntegerField(min_value=0)
    )

    # def create(self, validated_data):
    #     # self.instance
    #     print(validated_data)
    #     # organization

    def validate(self, attrs):
        users = attrs.get('pks')
        print(users)

        for ID in users:
            User.objects.filter(pk=ID).exists()

        return attrs
