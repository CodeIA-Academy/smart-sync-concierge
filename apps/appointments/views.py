"""
Views for appointments API.
Implements CRUD endpoints and appointment-specific operations.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .serializers import (
    AppointmentDetailSerializer,
    AppointmentCreateSerializer,
    AppointmentRescheduleSerializer,
    AppointmentListSerializer,
    AppointmentSuccessResponseSerializer,
    AppointmentConflictResponseSerializer,
)
from config.exceptions import ConflictException, InsufficientInfoException


class AppointmentPagination(PageNumberPagination):
    """Pagination for appointment lists."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class AppointmentViewSet(viewsets.ViewSet):
    """
    ViewSet for appointment management.

    Handles:
    - list: Get all appointments (with filtering)
    - create: Create new appointment from natural language prompt
    - retrieve: Get appointment details
    - update: Update appointment (full)
    - partial_update: Partial appointment update
    - destroy: Cancel appointment
    - reschedule: Reschedule an existing appointment
    - availability: Get available slots for rescheduling
    - conflicts: Check for conflicts
    """

    permission_classes = [IsAuthenticated]
    pagination_class = AppointmentPagination

    def get_serializer(self, *args, **kwargs):
        """Dynamically select serializer based on action."""
        if self.action == 'create':
            return AppointmentCreateSerializer(*args, **kwargs)
        elif self.action == 'reschedule':
            return AppointmentRescheduleSerializer(*args, **kwargs)
        elif self.action in ['list']:
            return AppointmentListSerializer(*args, **kwargs)
        else:
            return AppointmentDetailSerializer(*args, **kwargs)

    def list(self, request):
        """
        List all appointments with optional filtering.

        Query Parameters:
        - status: Filter by status (pending, confirmed, cancelled, completed)
        - fecha_inicio: Filter by start date (YYYY-MM-DD)
        - fecha_fin: Filter by end date (YYYY-MM-DD)
        - contacto_id: Filter by contact ID
        - page: Page number (default: 1)
        - page_size: Items per page (default: 20, max: 100)
        """
        from data.stores import AppointmentStore

        store = AppointmentStore()
        appointments = store.list_all()

        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            appointments = [apt for apt in appointments if apt.get('status') == status_filter]

        fecha_inicio = request.query_params.get('fecha_inicio')
        if fecha_inicio:
            appointments = [apt for apt in appointments if apt.get('fecha') >= fecha_inicio]

        fecha_fin = request.query_params.get('fecha_fin')
        if fecha_fin:
            appointments = [apt for apt in appointments if apt.get('fecha') <= fecha_fin]

        contacto_id = request.query_params.get('contacto_id')
        if contacto_id:
            appointments = [
                apt for apt in appointments
                if any(p.get('id') == contacto_id for p in apt.get('participantes', []))
            ]

        # Paginate
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(appointments, request)

        serializer = AppointmentListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        """
        Create a new appointment from natural language prompt.

        Expected input:
        {
            "prompt": "cita mañana 10am con Dr. Pérez",
            "user_timezone": "America/Mexico_City",
            "user_id": "user123"  # optional
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from data.stores import AppointmentStore, ContactStore, ServiceStore

        # Parse the prompt (simplified for MVP)
        # In production, this would use AI agents
        apt_data = self._parse_appointment_prompt(
            serializer.validated_data['prompt'],
            serializer.validated_data.get('user_timezone', 'America/Mexico_City'),
        )

        # Validate contact exists
        contact_store = ContactStore()
        contact = contact_store.get_by_id(apt_data.get('contact_id'))
        if not contact:
            return Response({
                'status': 'error',
                'code': 'NOT_FOUND',
                'message': f"Contact {apt_data.get('contact_id')} not found"
            }, status=status.HTTP_404_NOT_FOUND)

        # Validate service exists
        service_store = ServiceStore()
        service = service_store.get_by_id(apt_data.get('service_id'))
        if not service:
            return Response({
                'status': 'error',
                'code': 'NOT_FOUND',
                'message': f"Service {apt_data.get('service_id')} not found"
            }, status=status.HTTP_404_NOT_FOUND)

        # Check for conflicts
        apt_store = AppointmentStore()
        conflicts = apt_store.check_conflicts(apt_data)

        if conflicts:
            return Response({
                'status': 'error',
                'code': 'CONFLICT',
                'message': 'Requested time slot has conflicts',
                'details': conflicts,
                'suggestions': apt_store.get_suggestions(apt_data)
            }, status=status.HTTP_409_CONFLICT)

        # Create appointment
        appointment = apt_store.create(apt_data)

        return Response({
            'status': 'success',
            'data': AppointmentDetailSerializer(appointment).data,
            'message': 'Appointment created successfully',
            '_links': {
                'self': f'/api/v1/appointments/{appointment["id"]}/',
                'reschedule': f'/api/v1/appointments/{appointment["id"]}/reschedule/',
                'contact': f'/api/v1/contacts/{apt_data["contact_id"]}/',
            }
        }, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Get appointment details by ID."""
        from data.stores import AppointmentStore

        store = AppointmentStore()
        appointment = store.get_by_id(pk)

        if not appointment:
            return Response({
                'status': 'error',
                'code': 'NOT_FOUND',
                'message': f'Appointment {pk} not found'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = AppointmentDetailSerializer(appointment)
        return Response({
            'status': 'success',
            'data': serializer.data,
            '_links': {
                'self': f'/api/v1/appointments/{pk}/',
                'reschedule': f'/api/v1/appointments/{pk}/reschedule/',
            }
        })

    def update(self, request, pk=None):
        """Update entire appointment (PUT)."""
        from data.stores import AppointmentStore

        store = AppointmentStore()
        appointment = store.get_by_id(pk)

        if not appointment:
            return Response({
                'status': 'error',
                'code': 'NOT_FOUND',
                'message': f'Appointment {pk} not found'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = AppointmentDetailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated = store.update(pk, serializer.validated_data)

        return Response({
            'status': 'success',
            'data': AppointmentDetailSerializer(updated).data,
            'message': 'Appointment updated successfully'
        })

    def partial_update(self, request, pk=None):
        """Partial appointment update (PATCH)."""
        from data.stores import AppointmentStore

        store = AppointmentStore()
        appointment = store.get_by_id(pk)

        if not appointment:
            return Response({
                'status': 'error',
                'code': 'NOT_FOUND',
                'message': f'Appointment {pk} not found'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = AppointmentDetailSerializer(
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        updated = store.update(pk, serializer.validated_data)

        return Response({
            'status': 'success',
            'data': AppointmentDetailSerializer(updated).data,
            'message': 'Appointment updated successfully'
        })

    def destroy(self, request, pk=None):
        """Cancel/soft-delete an appointment."""
        from data.stores import AppointmentStore

        store = AppointmentStore()
        appointment = store.get_by_id(pk)

        if not appointment:
            return Response({
                'status': 'error',
                'code': 'NOT_FOUND',
                'message': f'Appointment {pk} not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete: mark as cancelled
        store.update(pk, {'status': 'cancelled'})

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
        """
        Reschedule an existing appointment.

        Expected input:
        {
            "fecha": "2026-01-25",
            "hora_inicio": "14:00",
            "hora_fin": "15:00",
            "notas": "Conflicto con otra cita"
        }
        """
        from data.stores import AppointmentStore

        store = AppointmentStore()
        appointment = store.get_by_id(pk)

        if not appointment:
            return Response({
                'status': 'error',
                'code': 'NOT_FOUND',
                'message': f'Appointment {pk} not found'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = AppointmentRescheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Prepare new appointment data
        apt_data = {
            **appointment,
            **serializer.validated_data
        }

        # Check for conflicts with new time
        conflicts = store.check_conflicts(apt_data, exclude_id=pk)

        if conflicts:
            return Response({
                'status': 'error',
                'code': 'CONFLICT',
                'message': 'Requested time slot has conflicts',
                'details': conflicts,
                'suggestions': store.get_suggestions(apt_data)
            }, status=status.HTTP_409_CONFLICT)

        # Update appointment
        updated = store.update(pk, apt_data)

        return Response({
            'status': 'success',
            'data': AppointmentDetailSerializer(updated).data,
            'message': 'Appointment rescheduled successfully',
            '_links': {
                'self': f'/api/v1/appointments/{pk}/',
            }
        })

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """
        Get available slots for rescheduling this appointment.

        Query Parameters:
        - dias_adelante: Number of days ahead to check (default: 7)
        """
        from data.stores import AppointmentStore, ContactStore

        store = AppointmentStore()
        appointment = store.get_by_id(pk)

        if not appointment:
            return Response({
                'status': 'error',
                'code': 'NOT_FOUND',
                'message': f'Appointment {pk} not found'
            }, status=status.HTTP_404_NOT_FOUND)

        dias_adelante = int(request.query_params.get('dias_adelante', 7))

        # Get contact to check availability
        contact_id = None
        for participant in appointment.get('participantes', []):
            if participant.get('rol') == 'prestador':
                contact_id = participant.get('id')
                break

        if not contact_id:
            return Response({
                'status': 'error',
                'code': 'NOT_FOUND',
                'message': 'No provider found for this appointment'
            }, status=status.HTTP_400_BAD_REQUEST)

        contact_store = ContactStore()
        available_slots = contact_store.get_available_slots(
            contact_id,
            days_ahead=dias_adelante
        )

        return Response({
            'status': 'success',
            'data': {
                'appointment_id': pk,
                'provider_id': contact_id,
                'available_slots': available_slots,
                'duration_minutes': appointment.get('duracion_minutos', 60)
            },
            '_links': {
                'self': f'/api/v1/appointments/{pk}/availability/',
                'reschedule': f'/api/v1/appointments/{pk}/reschedule/',
            }
        })

    def _parse_appointment_prompt(self, prompt, timezone):
        """
        Parse natural language appointment prompt.

        In MVP, this is a simplified version. In production,
        this would use AI agents for advanced parsing.

        Returns:
        {
            'fecha': 'YYYY-MM-DD',
            'hora_inicio': 'HH:MM',
            'hora_fin': 'HH:MM',
            'contact_id': 'contact_xxxxx',
            'service_id': 'service_xxxxx',
            'participantes': [...],
            'ubicacion': {...},
        }
        """
        # TODO: Implement AI-powered parsing
        # For MVP, return basic structure
        return {
            'fecha': None,
            'hora_inicio': None,
            'hora_fin': None,
            'contact_id': None,
            'service_id': None,
            'status': 'pending',
            'prompt_original': prompt,
            'zona_horaria': timezone,
        }
