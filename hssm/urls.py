from django.urls import path

from .views import views, auth, rest


urlpatterns = [
    path('login', auth.login, name='login'),
    path('logout', auth.logout, name='logout'),

    path('', views.index, name='index'),
    path('profile', views.profile, name='profile'),
    path('settings', views.settings, name='settings'),

    path('<str:of>/all', views.all, name='all'),  # of = students or staff

    path('admission/<int:adNum>', rest.admission, name='admission'),
    path('fees/<int:special>', rest.fees, name='fees'),
    path('classes', rest.classes),

    path('<str:of>/new', views.new, name='new'),
    path('<str:of>/<int:adNum>', views.view, name='view'),

    path('<str:of>/<int:adNum>/edit/', views.edit, name='edit'),

    path('assign_classes', views.assign_classes, name='assign_classes'),
    path('report/<str:r>', views.report, name='report'),
    path('certificate/<str:c>', views.certificate, name='certificate'),

]
