from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
]

urlpatterns = [
    path('map/', views.map_view, name='map_view'),
    path('api/location/', views.get_latest_location, name='get_latest_location'),
]