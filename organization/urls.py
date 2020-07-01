from django.urls import path, include
from .views import OrganizationViewSet
from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'orgs', OrganizationViewSet, basename='org')

urlpatterns = [
    path('', include(router.urls)),
]