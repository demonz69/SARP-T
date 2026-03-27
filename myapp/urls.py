from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # ── Student / Bus APIs ────────────────────────────────────
    path('api/location/', views.get_latest_location, name='api_location'),
    path('api/eta/', views.get_eta, name='api_eta'),
    path('api/gps/', views.receive_gps, name='receive_gps'),
    path('api/feedback/', views.submit_feedback, name='submit_feedback'),
    path('api/alert/<int:alert_id>/ack/', views.acknowledge_alert, name='ack_alert'),

    # ── Admin — single dashboard ──────────────────────────────
    path('manage/', admin_views.admin_dashboard, name='admin_dashboard'),

    # Users
    path('manage/users/<int:user_id>/edit/', admin_views.user_edit, name='admin_user_edit'),
    path('manage/users/<int:user_id>/delete/', admin_views.user_delete, name='admin_user_delete'),

    # Trips
    path('manage/trips/new/', admin_views.trip_create, name='admin_trip_create'),
    path('manage/trips/<int:trip_id>/edit/', admin_views.trip_edit, name='admin_trip_edit'),
    path('manage/trips/<int:trip_id>/delete/', admin_views.trip_delete, name='admin_trip_delete'),

    # Alerts
    path('manage/alerts/<int:alert_id>/ack/', admin_views.alert_ack, name='admin_alert_ack'),
    path('manage/alerts/ack-all/', admin_views.alert_ack_all, name='admin_alert_ack_all'),

    # Feedback
    path('manage/feedback/<int:fb_id>/delete/', admin_views.feedback_delete, name='admin_feedback_delete'),
]