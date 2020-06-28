from django.urls import path, include
from .views_api import UserRelatedView, ActivateUserView
from account import views
from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'users', UserRelatedView, basename='api')
app_name = 'account'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('user_login/', views.user_login, name='user_login'),
    path('activate/<int:pk>/<str:token>/', ActivateUserView.as_view()),
    path('', include(router.urls)),

]
