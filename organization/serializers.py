from rest_framework import serializers
from .models import Organization
from account.serializers import UserSerializer


class OrganizationSerializer(serializers.ModelSerializer):
    owner = UserSerializer()

    # users = UserSerializer(many=True)

    class Meta:
        model = Organization
        fields = ['id', 'name', 'location', 'phone', 'owner']

    def create(self, validated_data):
        return Organization.objects.create(owner=self.context.get('request').user, **validated_data)


class OrganizationUsersSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True)

    class Meta:
        model = Organization
        fields = ['users']
