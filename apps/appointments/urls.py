"""
URL configuration for appointments API.
Endpoints for appointment CRUD, rescheduling, and availability checks.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'appointments'

router = DefaultRouter()
router.register(r'appointments', views.AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', include(router.urls)),
]
