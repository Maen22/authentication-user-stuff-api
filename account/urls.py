from django.urls import path, include

from .views import activation_sent_view
from .views_api import UserRelatedView, ActivateUserView
from account import views
from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'users', UserRelatedView, basename='api')
app_name = 'account'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('user_login/', views.user_login, name='user_login'),
    path('sent/', activation_sent_view, name="activation_sent"),
    path('activate/<int:pk>/<str:token>/', ActivateUserView.as_view(), name='activate'),
    path('', include(router.urls)),

]
