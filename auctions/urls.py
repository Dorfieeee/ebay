from django.urls import path, include, re_path

from . import views

#app_name = 'auctions'
urlpatterns = [
    path('', views.index, name='index'),
    path('user/<str:username>', views.profile, name='profile'),
    re_path(r'(?P<listing_slug>.{1,70}[0-9]{10})$', views.listing, name='listing'),
    path('<slug:category_slug>', views.category, name='category'),
    path('create/', views.create_listing, name='create_listing'),
    path('close/', views.close_listing, name='close_listing'),
    path('api/watchlist', views.watchlist, name='watchlist'),
    path('api/bid', views.bid, name='bid'),
]