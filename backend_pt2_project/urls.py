from django.contrib import admin
from django.urls import path

from Backend_pt2_app import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.index, name='index'),
    path("users/", views.getData),
]
