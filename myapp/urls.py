from django.urls import path
from . import views

urlpatterns = [
    # Main Pages
    path('', views.home, name='home'),             # Points to 127.0.0.1:8000/
    path('about/', views.about, name='about'),     # Points to 127.0.0.1:8000/about/
    
    # IoT / Map Pages
    path('map/', views.map_view, name='map_view'), # Points to 127.0.0.1:8000/map/
    path('api/location/', views.get_latest_location, name='get_latest_location'),
]