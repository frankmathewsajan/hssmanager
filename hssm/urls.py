from django.contrib import admin
from django.urls import path

from .views import views, auth

urlpatterns = [
    path('login', auth.login, name='login'),
    path('logout', auth.logout, name='logout'),
    

    path('', views.index, name='index'),
    path('profile', views.profile, name='profile'),
    path('settings', views.settings, name='settings'),

    path('data/<str:name>', views.data, name='data'),
]
