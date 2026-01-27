"""
URL configuration for services API.
Endpoints for service catalog CRUD operations.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'services'

router = DefaultRouter()
router.register(r'services', views.ServiceViewSet, basename='service')

urlpatterns = [
    path('', include(router.urls)),
]
