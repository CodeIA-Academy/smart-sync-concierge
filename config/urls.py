"""
Main URL configuration for Smart-Sync Concierge API.

Organizes all endpoints by domain:
- /api/v1/appointments/ - Appointment management
- /api/v1/contacts/ - Contact (doctor/staff/resource) management
- /api/v1/services/ - Service catalog
- /api/v1/availability/ - Availability queries
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

# API Root Information
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    Smart-Sync Concierge API Root.
    Provides information about available endpoints.
    """
    return Response({
        'status': 'success',
        'message': 'Smart-Sync Concierge API v1',
        'version': '0.1.0',
        'endpoints': {
            'appointments': request.build_absolute_uri('/api/v1/appointments/'),
            'contacts': request.build_absolute_uri('/api/v1/contacts/'),
            'services': request.build_absolute_uri('/api/v1/services/'),
            'availability': request.build_absolute_uri('/api/v1/availability/'),
            'admin': request.build_absolute_uri('/admin/'),
            'docs': {
                'openapi': '/docs/contracts/api/openapi.yaml',
                'swagger': '/docs/swagger/',
                'redoc': '/docs/redoc/',
            }
        },
        '_links': {
            'self': request.build_absolute_uri('/api/v1/'),
            'health': request.build_absolute_uri('/api/v1/health/'),
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint.
    Returns 200 if the API is running.
    """
    return Response({
        'status': 'healthy',
        'message': 'Smart-Sync Concierge API is running',
        'version': '0.1.0',
        'timestamp': None,
    })


urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),

    # API Root and Health
    path('api/v1/', api_root, name='api-root'),
    path('api/v1/health/', health_check, name='health-check'),

    # Apps URLs
    path('api/v1/', include('apps.appointments.urls')),
    path('api/v1/', include('apps.contacts.urls')),
    path('api/v1/', include('apps.services.urls')),
    path('api/v1/', include('apps.availability.urls')),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = 'config.views.error_404'
handler500 = 'config.views.error_500'
