"""
Views for services API.
Implements CRUD endpoints for service catalog management.
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .serializers import (
    ServiceDetailSerializer,
    ServiceCreateUpdateSerializer,
    ServiceListSerializer,
)


class ServicePagination(PageNumberPagination):
    """Pagination for service lists."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ServiceViewSet(viewsets.ViewSet):
    """
    ViewSet for service (appointment type) catalog management.

    Handles:
    - list: Get all services with filtering
    - create: Create new service type
    - retrieve: Get service details
    - update: Update entire service (PUT)
    - partial_update: Partial service update (PATCH)
    - destroy: Soft-delete service
    """

    permission_classes = [IsAuthenticated]
    pagination_class = ServicePagination

    def get_serializer(self, *args, **kwargs):
        """Dynamically select serializer based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return ServiceCreateUpdateSerializer(*args, **kwargs)
        elif self.action == 'list':
            return ServiceListSerializer(*args, **kwargs)
        else:
            return ServiceDetailSerializer(*args, **kwargs)

    def list(self, request):
        """
        List all services with optional filtering.

        Query Parameters:
        - categoria: Filter by category (medica, odontologia, laboratorio, etc.)
        - subcategoria: Filter by subcategory
        - activo: Filter by active status (true/false)
        - buscar: Search in nombre or descripcion
        - page: Page number (default: 1)
        - page_size: Items per page (default: 20, max: 100)
        """
        from .models import Service
        from django.db.models import Q

        # Start with all services
        queryset = Service.objects.all()

        # Apply filters
        categoria = request.query_params.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria=categoria)

        activo = request.query_params.get('activo')
        if activo:
            activo_bool = activo.lower() == 'true'
            queryset = queryset.filter(activo=activo_bool)

        buscar = request.query_params.get('buscar')
        if buscar:
            search_term = buscar.lower()
            queryset = queryset.filter(
                Q(nombre__icontains=search_term) |
                Q(descripcion__icontains=search_term)
            )

        # Paginate
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        serializer = ServiceListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        """Create a new service."""
        serializer = ServiceCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from data.stores import ServiceStore

        store = ServiceStore()
        service = store.create(serializer.validated_data)

        return Response({
            'status': 'success',
            'data': ServiceDetailSerializer(service).data,
            'message': 'Service created successfully',
            '_links': {
                'self': f'/api/v1/services/{service["id"]}/',
            }
        }, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Get service details by ID."""
        from data.stores import ServiceStore

        store = ServiceStore()
        service = store.get_by_id(pk)

        if not service:
            return Response({
                'status': 'error',
                'code': 'NOT_FOUND',
                'message': f'Service {pk} not found'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ServiceDetailSerializer(service)
        return Response({
            'status': 'success',
            'data': serializer.data,
            '_links': {
                'self': f'/api/v1/services/{pk}/',
            }
        })

    def update(self, request, pk=None):
        """Update entire service (PUT)."""
        from data.stores import ServiceStore

        store = ServiceStore()
        service = store.get_by_id(pk)

        if not service:
            return Response({
                'status': 'error',
                'code': 'NOT_FOUND',
                'message': f'Service {pk} not found'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ServiceCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated = store.update(pk, serializer.validated_data)

        return Response({
            'status': 'success',
            'data': ServiceDetailSerializer(updated).data,
            'message': 'Service updated successfully'
        })

    def partial_update(self, request, pk=None):
        """Partial service update (PATCH)."""
        from data.stores import ServiceStore

        store = ServiceStore()
        service = store.get_by_id(pk)

        if not service:
            return Response({
                'status': 'error',
                'code': 'NOT_FOUND',
                'message': f'Service {pk} not found'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ServiceCreateUpdateSerializer(
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        updated = store.update(pk, serializer.validated_data)

        return Response({
            'status': 'success',
            'data': ServiceDetailSerializer(updated).data,
            'message': 'Service updated successfully'
        })

    def destroy(self, request, pk=None):
        """Soft-delete a service (mark as inactive)."""
        from data.stores import ServiceStore

        store = ServiceStore()
        service = store.get_by_id(pk)

        if not service:
            return Response({
                'status': 'error',
                'code': 'NOT_FOUND',
                'message': f'Service {pk} not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete: mark as inactive
        store.update(pk, {'activo': False})

        return Response(status=status.HTTP_204_NO_CONTENT)
