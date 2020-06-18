from rest_framework import generics, authentication, permissions, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.generics import UpdateAPIView
from .serializers import UserSerializer, AuthTokenSerializer, PasswordChangeSerializer, CreateUserSerializer
from .models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins


class CreateUserView(generics.CreateAPIView):
    """
    A view for any API caller to create a new account ('POST')
    through the users/' url
    """

    serializer_class = CreateUserSerializer
    permission_classes = ()
    authentication_classes = ()


class AdminViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """
    A viewset for the super user to retrieve ('GET') or update ('PUT', 'PATCH') or soft delete ('DELETE') any user data
    through the users/<id>(optional)/' url
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.setPassword(request.data['new_password'])
        instance.save()
        return Response(status=status.HTTP_200_OK)


class CreateTokenView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    permission_classes = []
    authentication_classes = []


class RetrieveUpdateUserView(viewsets.GenericViewSet):
    """
    A view for the authenticated user to retrieve ('GET') or update ('PUT', 'PATCH') his data
    through the 'users/me/' url
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication, ]
    permission_classes = [permissions.IsAuthenticated, ]

    @action(detail=False, methods=['get'])
    def me(self, request):
        user = request.user
        serializer = UserSerializer(user)
        if user is None:
            return Response(serializer.errors,
                            status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.data, status=status.HTTP_200_OK)


class DestroyUserView(generics.DestroyAPIView):
    """
    A view for the authenticated user to soft delete ('DELETE) his account (is_active = False)
    through the 'users/delete/me/' url
    """

    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def destroy(self, request, *args, **kwargs):
        instance = request.user
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(UpdateAPIView):
    """
    A view for the authenticated user to update his password ('PUT')
    through the 'users/change-password/' url
    """

    queryset = User.objects.all()
    serializer_class = PasswordChangeSerializer
    authentication_classes = [authentication.TokenAuthentication, ]
    permission_classes = [permissions.IsAuthenticated, ]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            instance.set_password(serializer.data.get('new_password'))
            instance.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
