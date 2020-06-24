from django.shortcuts import get_object_or_404
from rest_framework import authentication, permissions, mixins
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from .serializers import UserSerializer, AuthTokenSerializer, PasswordChangeSerializer, CreateUserSerializer, \
    UpdateUserSerializer
from .models import User
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator


class UserRelatedView(mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    """
    A view for the superusers and authenticated users to retrieve ('GET') or update ('PUT', 'PATCH') or soft delete (
    'DELETE') the users data through the users/ url for superusers, and 'users/me/' url for the authenticated users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'pk'

    def update(self, request, pk=None):
        user = get_object_or_404(self.queryset, pk=pk)
        serializer = UpdateUserSerializer(data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance=user, validated_data=serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        user = get_object_or_404(self.queryset, pk=pk)
        serializer = UpdateUserSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance=user, validated_data=serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        user = get_object_or_404(self.queryset, pk=pk)
        user.is_active = False
        user.save()
        return Response('Object deactivated successfully', status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def create_user(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.create(validated_data=serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_id': user.id})

    @action(detail=False, methods=['put'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        instance = serializer.validated_data['user']
        instance.set_password(serializer.data.get('new_password'))
        instance.save()

        return Response('Password changed successfully')

    # url_path for customizing all the methods
    @action(detail=False, methods=['get', 'put', 'patch', 'delete'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):

        user = request.user

        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'PUT':
            serializer = UpdateUserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.update(instance=user, validated_data=serializer.validated_data)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        if request.method == 'PATCH':
            serializer = UpdateUserSerializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.update(instance=user, validated_data=serializer.validated_data)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        if request.method == 'DELETE':
            user.is_active = False
            user.save()
            return Response("User is deactivated", status=status.HTTP_204_NO_CONTENT)
