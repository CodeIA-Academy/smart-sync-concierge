"""
URL configuration for contacts API.
Endpoints for contact CRUD and availability management.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'contacts'

router = DefaultRouter()
router.register(r'contacts', views.ContactViewSet, basename='contact')

urlpatterns = [
    path('', include(router.urls)),
]
