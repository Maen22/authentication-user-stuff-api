from django.urls import path, include
from .views import CreateUserView, CreateTokenView, ManageUserView, AccountList, AccountSoftDelete
from .views import SuperViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

app_name = 'user'

router.register(r'super', SuperViewSet, basename='super')

urlpatterns = [
    path('', CreateUserView.as_view(), name='create'),
    path('login/', CreateTokenView.as_view(), name='token'),
    path('me/', ManageUserView.as_view(), name='me'),
    path('get/', AccountList.as_view(), name='list'),
    path('super/', include(router.urls))
]
