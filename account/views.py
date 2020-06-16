from rest_framework import generics, authentication, permissions, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import UpdateAPIView
from rest_framework.settings import api_settings
from .serializers import UserSerializer, AuthTokenSerializer, PasswordChangeSerializer
from .models import Account
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


# # class AccountList(generics.ListAPIView):
# #     queryset = Account.objects.all()
# #     serializer_class = UserSerializer
# #     authentication_classes = (authentication.TokenAuthentication,)
# #     permission_classes = (permissions.IsAdminUser,)
# #
# #
# # class AccountSoftDelete(generics.DestroyAPIView):
# #     serializer_class = UserSerializer
# #     authentication_classes = (authentication.TokenAuthentication,)
# #     permission_classes = (permissions.IsAdminUser,)
#
#     def delete(self, request, *args, **kwargs):
#         user = Account.objects.get(id=request.id)
#         user.is_active = False
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class ManageUserView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
#     serializer_class = UserSerializer
#     authentication_classes = (authentication.TokenAuthentication,)
#     permission_classes = (permissions.IsAuthenticated,)
#
#     def get_object(self):
#         return self.request.user


class SuperViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = Account.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.setPassword(request.data['new_password'])
        instance.save()
        return Response(status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(UpdateAPIView):
    """
    The update view for changing the user password.
    The user should provide the old password, new password, and a confirm for the new one.
    """

    model = Account
    serializer_class = PasswordChangeSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

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
