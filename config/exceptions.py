"""
Custom exception handlers for Smart-Sync Concierge API.
Provides consistent error response formatting.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from .constants import (
    ERROR_CODE_INVALID_REQUEST,
    ERROR_CODE_CONFLICT,
    ERROR_CODE_NOT_FOUND,
)


class SmartSyncException(APIException):
    """Base exception for Smart-Sync Concierge API."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Un error ocurrió'
    default_code = 'error'

    def __init__(self, detail=None, code=None, status_code=None):
        if status_code is not None:
            self.status_code = status_code
        super().__init__(detail, code)


class ConflictException(SmartSyncException):
    """Exception for appointment conflicts (overlaps, unavailability)."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Conflicto: El horario no está disponible'
    default_code = ERROR_CODE_CONFLICT

    def __init__(self, detail=None, conflict_type=None, suggestions=None):
        self.conflict_type = conflict_type
        self.suggestions = suggestions or []
        super().__init__(detail)


class InvalidAppointmentException(SmartSyncException):
    """Exception for invalid appointment data."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Datos de cita inválidos'
    default_code = ERROR_CODE_INVALID_REQUEST


class ResourceNotFoundException(SmartSyncException):
    """Exception when resource is not found."""

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Recurso no encontrado'
    default_code = ERROR_CODE_NOT_FOUND


class InsufficientInfoException(SmartSyncException):
    """Exception for ambiguous or insufficient information in prompt."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'El prompt es ambiguo y requiere más información'
    default_code = 'INSUFFICIENT_INFO'

    def __init__(self, detail=None, ambiguities=None):
        self.ambiguities = ambiguities or []
        super().__init__(detail)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF.
    Provides consistent error response formatting across the API.
    """

    # Import here to avoid circular imports
    from rest_framework.views import exception_handler

    # Get the standard DRF exception response
    response = exception_handler(exc, context)

    # If response is None, it's an unhandled exception
    if response is None:
        return Response({
            'status': 'error',
            'code': 'INTERNAL_ERROR',
            'message': 'Un error interno ocurrió',
            'details': str(exc) if str(exc) else 'Unknown error',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Standardize error response format
    if isinstance(exc, ConflictException):
        return Response({
            'status': 'error',
            'code': exc.default_code,
            'message': str(exc.detail) if hasattr(exc, 'detail') else exc.default_detail,
            'details': {
                'conflict_type': exc.conflict_type,
            },
            'suggestions': exc.suggestions,
        }, status=exc.status_code)

    elif isinstance(exc, InsufficientInfoException):
        return Response({
            'status': 'error',
            'code': exc.default_code,
            'message': str(exc.detail) if hasattr(exc, 'detail') else exc.default_detail,
            'ambiguities': exc.ambiguities,
        }, status=exc.status_code)

    elif isinstance(exc, ResourceNotFoundException):
        return Response({
            'status': 'error',
            'code': exc.default_code,
            'message': str(exc.detail) if hasattr(exc, 'detail') else exc.default_detail,
        }, status=exc.status_code)

    # Handle validation errors
    if response.status_code == status.HTTP_400_BAD_REQUEST:
        # Extract validation errors
        validation_errors = []
        if isinstance(response.data, dict):
            for field, errors in response.data.items():
                if isinstance(errors, list):
                    for error in errors:
                        validation_errors.append({
                            'field': field,
                            'message': str(error),
                        })
                else:
                    validation_errors.append({
                        'field': field,
                        'message': str(errors),
                    })

        return Response({
            'status': 'error',
            'code': ERROR_CODE_INVALID_REQUEST,
            'message': 'Solicitud inválida',
            'details': validation_errors,
        }, status=status.HTTP_400_BAD_REQUEST)

    # Handle 404 Not Found
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return Response({
            'status': 'error',
            'code': ERROR_CODE_NOT_FOUND,
            'message': 'Recurso no encontrado',
        }, status=status.HTTP_404_NOT_FOUND)

    # Handle 401 Unauthorized
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return Response({
            'status': 'error',
            'code': 'UNAUTHORIZED',
            'message': 'No autorizado. Se requiere autenticación.',
        }, status=status.HTTP_401_UNAUTHORIZED)

    # Handle 403 Forbidden
    if response.status_code == status.HTTP_403_FORBIDDEN:
        return Response({
            'status': 'error',
            'code': 'FORBIDDEN',
            'message': 'Acceso prohibido.',
        }, status=status.HTTP_403_FORBIDDEN)

    # Handle 429 Too Many Requests (Rate Limiting)
    if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        return Response({
            'status': 'error',
            'code': 'RATE_LIMIT_EXCEEDED',
            'message': 'Demasiadas solicitudes. Por favor, espera antes de intentar de nuevo.',
            'retry_after': response.get('Retry-After', 60),
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)

    # Handle 500 Internal Server Error
    if response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        return Response({
            'status': 'error',
            'code': 'INTERNAL_ERROR',
            'message': 'Un error interno del servidor ocurrió',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Default: return standardized successful response
    if response.status_code in [
        status.HTTP_200_OK,
        status.HTTP_201_CREATED,
        status.HTTP_202_ACCEPTED,
    ]:
        return Response({
            'status': 'success',
            'data': response.data,
        }, status=response.status_code)

    return response
