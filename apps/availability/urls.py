"""
URL configuration for availability API.
Endpoints for checking availability and scheduling.
"""

from django.urls import path
from . import views

app_name = 'availability'

urlpatterns = [
    path('availability/check/', views.check_availability, name='check-availability'),
    path('availability/suggest/', views.suggest_times, name='suggest-times'),
    path('availability/schedule/<str:contacto_id>/', views.get_contact_schedule, name='get-schedule'),
]
