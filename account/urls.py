from django.urls import path, include
from .views import UserRelatedView
from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'users', UserRelatedView, basename='api')

urlpatterns = [
    path('', include(router.urls)),
]
