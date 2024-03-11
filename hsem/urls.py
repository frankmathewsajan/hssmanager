from django.contrib import admin
from django.urls import path, include
from .views import views, auth

urlpatterns = [
    path("login/", auth.login_view, name="login"),
    path("logout/", auth.logout_view, name="logout"),

    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
]
