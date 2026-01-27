"""
Custom view handlers for Smart-Sync Concierge API.
Handles custom error pages and API responses.
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
def error_404(request, exception=None):
    """
    Custom 404 error handler.
    Returns JSON response instead of HTML.
    """
    return Response({
        'status': 'error',
        'code': 'NOT_FOUND',
        'message': f'El recurso solicitado no existe: {request.path}',
    }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
def error_500(request):
    """
    Custom 500 error handler.
    Returns JSON response instead of HTML.
    """
    return Response({
        'status': 'error',
        'code': 'INTERNAL_ERROR',
        'message': 'Un error interno del servidor ocurrió',
        'support': 'Por favor contacta al equipo de soporte',
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
