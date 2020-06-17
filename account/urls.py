from django.urls import path, include
from .views import CreateUserView, CreateTokenView, ChangePasswordView, RetrieveUpdateUserView, DestroyUserView, \
    AdminViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

app_name = 'user'

router.register(r'', AdminViewSet, basename='super')

urlpatterns = [

    # Registration endpoint ('POST')
    path('', CreateUserView.as_view(), name='create'),

    # Admin endpoints ('GET', 'PUT', 'PATCH', 'DELETE')
    path('', include(router.urls)),


    path('login/', CreateTokenView.as_view(), name='token'),

    path('me/', DestroyUserView.as_view(), name='destroy_me'),
    path('me/', RetrieveUpdateUserView.as_view(), name='retrieve_update_me'),
    path('change_password/', ChangePasswordView.as_view(), name='password')

]
