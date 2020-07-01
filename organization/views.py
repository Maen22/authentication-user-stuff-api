from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from account.models import User
from .models import Organization
from .serializers import OrganizationSerializer, OrganizationUsersSerializer


class OrganizationViewSet(mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.ListModelMixin,
                          GenericViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # def list(self, request, *args, **kwargs):
    #     # queryset = self.filter_queryset(self.get_queryset())
    #     #
    #     # serializer = self.get_serializer(queryset, many=True)
    #     # # print(serializer.data)
    #     # for n in range(len(serializer.data)):
    #     #     serializer.data[n]['owner'] = User.objects.get(id=serializer.data[n]['owner']).first_name
    #     #     serializer.data.append({'users': Organization.objects.get()})
    #     # return Response(serializer.data)
    #
    #     pass

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def list_users(self, request, pk=None):
        org = get_object_or_404(Organization, pk=pk)
        serializer = OrganizationUsersSerializer(org)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def create_org(self, request):
        serializer = OrganizationSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.create(validated_data=serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
