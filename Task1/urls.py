from django.contrib import admin
from django.urls import path, include
from rest_framework.documentation import include_docs_urls
from account import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('docs/', include_docs_urls('rest_framework.docs')),
    path('home/', views.index, name='index'),
    path('special/', views.special, name='special'),
    path('logout/', views.user_logout, name='logout'),
    path('', include('account.urls')),

]
