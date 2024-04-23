from django.contrib import admin
from django.urls import path

from .views import views, auth

urlpatterns = [
    path('login', auth.login, name='login'),
    path('logout', auth.logout, name='logout'),
    

    path('', views.index, name='index'),
    path('profile', views.profile, name='profile'),
    path('settings', views.settings, name='settings'),

    path('<str:of>/all', views.all, name='all'), # of = students or staff
    path('admission/<int:adNum>', views.admission, name='admission'),
    path('fees/<int:special>', views.fees, name='fees'),

    path('<str:of>/new', views.new, name='new'),
    path('<str:of>/<int:adNum>', views.view, name='view'),

    path('<str:of>/<int:adNum>/edit/', views.edit, name='edit'),

    

    
]
