"""
Views for availability API.
Implements availability checking and scheduling endpoints.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.contacts.serializers import ContactAvailabilitySerializer


@api_view(['POST'])
def check_availability(request):
    """
    Check combined availability for a specific contact and service.

    Expected input:
    {
        "contacto_id": "contact_dr_perez",
        "servicio_id": "service_consulta",
        "fecha": "2026-01-25",
        "hora_inicio": "14:00",
        "hora_fin": "15:00",  # optional
        "ubicacion_id": "loc_consultorio_1"  # optional
    }

    Returns available slots if requested time is not available.
    """
    from data.stores import ContactStore, ServiceStore, AppointmentStore

    # Validate input
    serializer = ContactAvailabilitySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    contacto_id = request.data.get('contacto_id')
    servicio_id = request.data.get('servicio_id')
    fecha = serializer.validated_data['fecha']
    hora_inicio = serializer.validated_data['hora_inicio']
    hora_fin = serializer.validated_data.get('hora_fin')
    ubicacion_id = serializer.validated_data.get('ubicacion_id')

    # Verify contact exists
    contact_store = ContactStore()
    contact = contact_store.get_by_id(contacto_id)
    if not contact:
        return Response({
            'status': 'error',
            'code': 'NOT_FOUND',
            'message': f'Contact {contacto_id} not found'
        }, status=status.HTTP_404_NOT_FOUND)

    # Verify service exists
    if servicio_id:
        service_store = ServiceStore()
        service = service_store.get_by_id(servicio_id)
        if not service:
            return Response({
                'status': 'error',
                'code': 'NOT_FOUND',
                'message': f'Service {servicio_id} not found'
            }, status=status.HTTP_404_NOT_FOUND)

    # Check contact availability
    is_available, razon = contact_store.check_availability(
        contacto_id,
        fecha,
        hora_inicio,
        hora_fin,
        ubicacion_id
    )

    # Check for appointment conflicts
    apt_store = AppointmentStore()
    apt_data = {
        'fecha': fecha,
        'hora_inicio': hora_inicio,
        'hora_fin': hora_fin or hora_inicio,
        'participantes': [{'id': contacto_id}]
    }
    conflicts = apt_store.check_conflicts(apt_data)

    response_data = {
        'contacto_id': contacto_id,
        'fecha': fecha,
        'hora_inicio': hora_inicio,
        'disponible': is_available and not conflicts,
    }

    if not is_available:
        response_data['razon'] = razon

    if conflicts:
        response_data['conflictos'] = conflicts

    # Get available slots if not available
    if not is_available or conflicts:
        slots = contact_store.get_available_slots(contacto_id, days_ahead=7)
        response_data['slots_disponibles'] = slots

    return Response({
        'status': 'success',
        'data': response_data,
        '_links': {
            'self': '/api/v1/availability/check/',
        }
    })


@api_view(['POST'])
def suggest_times(request):
    """
    Get suggested available time slots for a contact and service.

    Expected input:
    {
        "contacto_id": "contact_dr_perez",
        "servicio_id": "service_consulta",
        "fecha_preferida": "2026-01-25",  # optional
        "dias_adelante": 7,  # optional, default: 7
        "duracion_minutos": 60,  # optional, default from service
        "ubicacion_id": "loc_consultorio_1"  # optional
    }

    Returns list of suggested time slots with confidence scores.
    """
    from data.stores import ContactStore, ServiceStore

    contacto_id = request.data.get('contacto_id')
    servicio_id = request.data.get('servicio_id')
    dias_adelante = int(request.data.get('dias_adelante', 7))
    duracion_minutos = int(request.data.get('duracion_minutos', 60))
    ubicacion_id = request.data.get('ubicacion_id')

    # Verify contact exists
    contact_store = ContactStore()
    contact = contact_store.get_by_id(contacto_id)
    if not contact:
        return Response({
            'status': 'error',
            'code': 'NOT_FOUND',
            'message': f'Contact {contacto_id} not found'
        }, status=status.HTTP_404_NOT_FOUND)

    # Get service info if provided
    service = None
    if servicio_id:
        service_store = ServiceStore()
        service = service_store.get_by_id(servicio_id)
        if not service:
            return Response({
                'status': 'error',
                'code': 'NOT_FOUND',
                'message': f'Service {servicio_id} not found'
            }, status=status.HTTP_404_NOT_FOUND)
        duracion_minutos = service.get('duracion_minutos', duracion_minutos)

    # Get available slots
    slots = contact_store.get_available_slots(
        contacto_id,
        days_ahead=dias_adelante,
        duration_minutes=duracion_minutos,
        location_id=ubicacion_id
    )

    return Response({
        'status': 'success',
        'data': {
            'contacto_id': contacto_id,
            'servicio_id': servicio_id,
            'duracion_minutos': duracion_minutos,
            'slots_sugeridos': slots,
        },
        '_links': {
            'self': '/api/v1/availability/suggest/',
        }
    })


@api_view(['GET'])
def get_contact_schedule(request, contacto_id):
    """
    Get the complete schedule for a contact.

    Query Parameters:
    - ubicacion_id: Filter by specific location
    """
    from data.stores import ContactStore

    contact_store = ContactStore()
    contact = contact_store.get_by_id(contacto_id)

    if not contact:
        return Response({
            'status': 'error',
            'code': 'NOT_FOUND',
            'message': f'Contact {contacto_id} not found'
        }, status=status.HTTP_404_NOT_FOUND)

    ubicacion_id = request.query_params.get('ubicacion_id')

    # Get schedule/locations
    locations = contact.get('ubicaciones', [])
    if ubicacion_id:
        locations = [loc for loc in locations if loc.get('id') == ubicacion_id]

    return Response({
        'status': 'success',
        'data': {
            'contacto_id': contacto_id,
            'nombre': contact.get('nombre'),
            'tipo': contact.get('tipo'),
            'ubicaciones': locations,
        },
        '_links': {
            'self': f'/api/v1/availability/schedule/{contacto_id}/',
        }
    })
