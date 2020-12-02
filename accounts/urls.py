from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='user_login'),
    path('logout/', auth_views.LogoutView.as_view(), name='user_logout'),
    path('register/', views.register, name='register'),
    path('watchlist', views.watchlist, name='my-watchlist'),
    path('my-profile', views.my_profile, name='my-profile'),
    path('active-listings', views.active_listings, name='active-listings'),
    path('non-active-listings', views.non_active_listings, name='non-active-listings'),
    path('', views.dashboard, name='dashboard'),
]