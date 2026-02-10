"""
URL configuration for services API.
Endpoints for service catalog CRUD operations.
"""

from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'services'

router = DefaultRouter()
router.register(r'services', views.ServiceViewSet, basename='service')

# Routes for string-based PKs must come BEFORE the router includes
# to prevent the router's default pattern from capturing them first
urlpatterns = [
    re_path(
        r'^services/(?P<pk>[a-zA-Z0-9_-]+)/$',
        views.ServiceViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='service-detail'
    ),
    path('', include(router.urls)),
]
