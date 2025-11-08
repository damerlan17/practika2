from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.user_profile, name='profile'),
    path('superadmin/', views.superadmin_panel, name='superadmin'),
    path('logout/', views.user_logout, name='logout'),
]
