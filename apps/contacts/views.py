"""
Views for contacts API.
Implements CRUD endpoints for contact management.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .serializers import (
    ContactDetailSerializer,
    ContactCreateUpdateSerializer,
    ContactListSerializer,
    ContactAvailabilitySerializer,
    ContactAvailabilityResponseSerializer,
)


class ContactPagination(PageNumberPagination):
    """Pagination for contact lists."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ContactViewSet(viewsets.ViewSet):
    """
    ViewSet for contact (doctor/staff/resource) management.

    Handles:
    - list: Get all contacts with filtering
    - create: Create new contact
    - retrieve: Get contact details
    - update: Update entire contact (PUT)
    - partial_update: Partial contact update (PATCH)
    - destroy: Soft-delete contact
    - availability: Check contact availability for specific date/time
    - appointments: Get appointments for a contact
    """

    permission_classes = [IsAuthenticated]
    pagination_class = ContactPagination
    lookup_field = 'pk'  # Use 'pk' for string-based primary key matching

    def get_serializer(self, *args, **kwargs):
        """Dynamically select serializer based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return ContactCreateUpdateSerializer(*args, **kwargs)
        elif self.action == 'availability':
            return ContactAvailabilitySerializer(*args, **kwargs)
        elif self.action == 'list':
            return ContactListSerializer(*args, **kwargs)
        else:
            return ContactDetailSerializer(*args, **kwargs)

    def list(self, request):
        """
        List all contacts with optional filtering.

        Query Parameters:
        - tipo: Filter by type (doctor, staff, resource)
        - especialidad: Filter by specialty (for doctors)
        - activo: Filter by active status (true/false)
        - categoria: Filter by category (for resources)
        - buscar: Search in nombre or especialidad
        - page: Page number (default: 1)
        - page_size: Items per page (default: 20, max: 100)
        """
        from .models import Contact
        from django.db.models import Q

        # Start with all contacts
        queryset = Contact.objects.all()

        # Apply filters
        tipo = request.query_params.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)

        activo = request.query_params.get('activo')
        if activo:
            activo_bool = activo.lower() == 'true'
            queryset = queryset.filter(activo=activo_bool)

        buscar = request.query_params.get('buscar')
        if buscar:
            search_term = buscar.lower()
            queryset = queryset.filter(
                Q(nombre__icontains=search_term) |
                Q(titulo__icontains=search_term)
            )

        # Paginate
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        serializer = ContactListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        """Create a new contact."""
        serializer = ContactCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from data.stores import ContactStore

        store = ContactStore()
        contact = store.create(serializer.validated_data)

        return Response({
            'status': 'success',
            'data': ContactDetailSerializer(contact).data,
            'message': 'Contact created successfully',
            '_links': {
                'self': f'/api/v1/contacts/{contact["id"]}/',
                'availability': f'/api/v1/contacts/{contact["id"]}/availability/',
            }
        }, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Get contact details by ID."""
        from data.stores import ContactStore

        store = ContactStore()
        contact = store.get_by_id(pk)

        if not contact:
            return Response({
                'status': 'error',
                'code': 'NOT_FOUND',
                'message': f'Contact {pk} not found'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ContactDetailSerializer(contact)
        return Response({
            'status': 'success',
            'data': serializer.data,
            '_links': {
                'self': f'/api/v1/contacts/{pk}/',
                'availability': f'/api/v1/contacts/{pk}/availability/',
                'appointments': f'/api/v1/contacts/{pk}/appointments/',
            }
        })

    def update(self, request, pk=None):
        """Update entire contact (PUT)."""
        from data.stores import ContactStore

        store = ContactStore()
        contact = store.get_by_id(pk)

        if not contact:
            return Response({
                'status': 'error',
                'code': 'NOT_FOUND',
                'message': f'Contact {pk} not found'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ContactCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated = store.update(pk, serializer.validated_data)

        return Response({
            'status': 'success',
            'data': ContactDetailSerializer(updated).data,
            'message': 'Contact updated successfully'
        })

    def partial_update(self, request, pk=None):
        """Partial contact update (PATCH)."""
        from data.stores import ContactStore

        store = ContactStore()
        contact = store.get_by_id(pk)

        if not contact:
            return Response({
                'status': 'error',
                'code': 'NOT_FOUND',
                'message': f'Contact {pk} not found'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ContactCreateUpdateSerializer(
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        updated = store.update(pk, serializer.validated_data)

        return Response({
            'status': 'success',
            'data': ContactDetailSerializer(updated).data,
            'message': 'Contact updated successfully'
        })

    def destroy(self, request, pk=None):
        """Soft-delete a contact (mark as inactive)."""
        from data.stores import ContactStore

        store = ContactStore()
        contact = store.get_by_id(pk)

        if not contact:
            return Response({
                'status': 'error',
                'code': 'NOT_FOUND',
                'message': f'Contact {pk} not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete: mark as inactive
        store.update(pk, {'activo': False})

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def availability(self, request, pk=None):
        """
        Check contact availability for a specific date and time.

        Expected input:
        {
            "fecha": "2026-01-25",
            "hora_inicio": "14:00",
            "hora_fin": "15:00",
            "ubicacion_id": "loc_consultorio_1"  # optional
        }
        """
        from data.stores import ContactStore

        store = ContactStore()
        contact = store.get_by_id(pk)

        if not contact:
            return Response({
                'status': 'error',
                'code': 'NOT_FOUND',
                'message': f'Contact {pk} not found'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ContactAvailabilitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check availability
        is_available, razon = store.check_availability(
            pk,
            serializer.validated_data['fecha'],
            serializer.validated_data['hora_inicio'],
            serializer.validated_data.get('hora_fin'),
            serializer.validated_data.get('ubicacion_id')
        )

        response_data = {
            'disponible': is_available,
        }

        if not is_available:
            response_data['razon'] = razon

        # Get available slots if not available
        if not is_available:
            slots = store.get_available_slots(pk, days_ahead=3)
            response_data['slots_disponibles'] = slots

        return Response({
            'status': 'success',
            'data': response_data,
            '_links': {
                'self': f'/api/v1/contacts/{pk}/availability/',
            }
        })

    @action(detail=True, methods=['get'])
    def appointments(self, request, pk=None):
        """
        Get appointments for this contact.

        Query Parameters:
        - status: Filter by appointment status
        - fecha_inicio: Filter by start date
        - fecha_fin: Filter by end date
        - page: Page number
        - page_size: Items per page
        """
        from data.stores import ContactStore, AppointmentStore

        # Verify contact exists
        contact_store = ContactStore()
        contact = contact_store.get_by_id(pk)

        if not contact:
            return Response({
                'status': 'error',
                'code': 'NOT_FOUND',
                'message': f'Contact {pk} not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Get appointments for this contact
        apt_store = AppointmentStore()
        appointments = apt_store.list_by_contact(pk)

        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            appointments = [
                apt for apt in appointments
                if apt.get('status') == status_filter
            ]

        fecha_inicio = request.query_params.get('fecha_inicio')
        if fecha_inicio:
            appointments = [
                apt for apt in appointments
                if apt.get('fecha') >= fecha_inicio
            ]

        fecha_fin = request.query_params.get('fecha_fin')
        if fecha_fin:
            appointments = [
                apt for apt in appointments
                if apt.get('fecha') <= fecha_fin
            ]

        # Paginate
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(appointments, request)

        from .serializers import AppointmentListSerializer
        serializer = AppointmentListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
