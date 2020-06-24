from django.urls import path, include
from .views import UserRelatedView, ActivateUserView
from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'users', UserRelatedView, basename='api')

urlpatterns = [
    path('activate/<int:pk>/<str:token>/', ActivateUserView.as_view()),
    path('', include(router.urls)),
]
