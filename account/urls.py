from django.conf.urls import url
from django.urls import path, include
from .views import CreateUserView, CreateTokenView, ChangePasswordView, RetrieveUpdateUserView, DestroyUserView, \
    AdminViewSet, UpdateUser
from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'users', RetrieveUpdateUserView, basename='users')
# router.register('admins', AdminViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # path('create/', CreateUserView.as_view(), name='create_user'),
    # path('update/', UpdateUser.as_view(), name='update_user'),
    path('login/', CreateTokenView.as_view(), name='token'),
    # path('change_password/', ChangePasswordView.as_view(), name='password'),

]

# path('me/', DestroyUserView.as_view(), name='destroy_me'),
# path('me/', RetrieveUpdateUserView.as_view(), name='retrieve_update_me'),
# Registration endpoint ('POST')
# Admin endpoints ('GET', 'PUT', 'PATCH', 'DELETE')
