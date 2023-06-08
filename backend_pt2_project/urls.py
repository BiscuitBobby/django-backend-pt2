from django.contrib import admin
from django.urls import path

from Backend_pt2_app import views

urlpatterns = [
    path("admin/", admin.site.
         urls),
    path('', views.index, name='index'),
    path("users/", views.getData, name='getData'),
    path("add/", views.addUser, name='addData'),
    path("loc/", views.nearEvents, name='location'),
    path("eventupdate/", views.update_event, name='eventupdate'),
    path("auth/", views.auth, name='auth'),
    path("register/", views.register, name='register'),
    path("join/", views.event_join, name='join'),
    path("leave/", views.leave_event, name='leave')
]
