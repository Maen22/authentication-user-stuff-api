from django.shortcuts import get_object_or_404
from rest_framework import permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from account.models import User
from account.serializers import UserSerializer
from .models import Organization
from .serializers import OrganizationSerializer, AddingUsersSerializer


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 5


class OrganizationViewSet(mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.ListModelMixin,
                          GenericViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def list_users(self, request, pk=None):
        org = get_object_or_404(Organization, pk=pk)
        queryset = org.users.all()

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def create_org(self, request):
        serializer = OrganizationSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.create(validated_data=serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def add_users(self, request, pk=None):
        org = Organization.objects.get(pk=pk)
        serializer = AddingUsersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        users_list = list(org.users.all())
        for pk in serializer.validated_data['pks']:
            users_list.append(User.objects.get(pk=pk))
        org.users.set(users_list)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


