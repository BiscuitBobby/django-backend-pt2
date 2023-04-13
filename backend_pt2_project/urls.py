from django.contrib import admin
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from Backend_pt2_app import views

urlpatterns = [
    path("admin/", admin.site.
         urls),
    path('', views.index, name='index'),
    path("users/", views.getData, name='getData'),
    path("add/", views.addUser, name='addData'),
    path("loc/", views.nearEvents, name='location'),
    path("login/", views.login,name='login')
]
