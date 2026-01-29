"""
Views for agent decision traces.
Provides endpoints for viewing and analyzing AI agent decision traces.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination


class TracePagination(PageNumberPagination):
    """Pagination for trace lists."""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class TracesViewSet(viewsets.ViewSet):
    """
    ViewSet for agent decision traces.

    Provides observability into AI agent decision-making for debugging
    and analysis.

    Endpoints:
    - list: Get all traces (with filtering)
    - retrieve: Get trace details
    - by_status: Filter traces by status (success, error, conflict)
    - by_user: Filter traces by user
    """

    permission_classes = [IsAuthenticated]
    pagination_class = TracePagination

    def list(self, request):
        """
        List all agent decision traces.

        Query Parameters:
        - status: Filter by status (success, error, conflict)
        - user_id: Filter by user
        - page: Page number
        - page_size: Items per page
        """
        from data.stores import TraceStore
        store = TraceStore()
        traces = store.list_all()

        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            traces = [t for t in traces if t.get('final_status') == status_filter]

        user_id_filter = request.query_params.get('user_id')
        if user_id_filter:
            traces = [t for t in traces if t.get('user_id') == user_id_filter]

        # Sort by newest first
        traces.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        # Paginate
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(traces, request)

        if page is not None:
            serialized = [{
                'trace_id': t.get('trace_id'),
                'timestamp': t.get('timestamp'),
                'user_id': t.get('user_id'),
                'final_status': t.get('final_status'),
                'total_duration_ms': t.get('total_duration_ms'),
                'num_agents': len(t.get('agents', [])),
            } for t in page]
            return paginator.get_paginated_response(serialized)

        return Response({
            'count': len(traces),
            'results': traces,
        })

    def retrieve(self, request, pk=None):
        """
        Get trace details by ID.

        Returns complete trace with all agent decisions.
        """
        from data.stores import TraceStore
        store = TraceStore()
        trace = store.get_by_id(pk)

        if not trace:
            return Response({
                'status': 'error',
                'code': 'NOT_FOUND',
                'message': f'Trace {pk} not found',
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'status': 'success',
            'data': trace,
            '_links': {
                'self': f'/api/v1/traces/{pk}/',
                'list': '/api/v1/traces/',
            }
        })

    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """
        Filter traces by final status.

        Query Parameters:
        - status: success, error, or conflict (required)
        """
        status_filter = request.query_params.get('status')
        if not status_filter:
            return Response({
                'status': 'error',
                'message': 'status parameter is required',
            }, status=status.HTTP_400_BAD_REQUEST)

        from data.stores import TraceStore
        store = TraceStore()
        traces = store.list_by_status(status_filter)

        # Sort by newest first
        traces.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        # Paginate
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(traces, request)

        if page is not None:
            serialized = [{
                'trace_id': t.get('trace_id'),
                'timestamp': t.get('timestamp'),
                'user_id': t.get('user_id'),
                'final_status': t.get('final_status'),
                'total_duration_ms': t.get('total_duration_ms'),
            } for t in page]
            return paginator.get_paginated_response(serialized)

        return Response({
            'count': len(traces),
            'status': status_filter,
            'results': traces,
        })

    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """
        Filter traces by user ID.

        Query Parameters:
        - user_id: User identifier (required)
        """
        user_id_filter = request.query_params.get('user_id')
        if not user_id_filter:
            return Response({
                'status': 'error',
                'message': 'user_id parameter is required',
            }, status=status.HTTP_400_BAD_REQUEST)

        from data.stores import TraceStore
        store = TraceStore()
        traces = store.list_by_user(user_id_filter)

        # Sort by newest first
        traces.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        # Paginate
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(traces, request)

        if page is not None:
            serialized = [{
                'trace_id': t.get('trace_id'),
                'timestamp': t.get('timestamp'),
                'final_status': t.get('final_status'),
                'total_duration_ms': t.get('total_duration_ms'),
                'num_agents': len(t.get('agents', [])),
            } for t in page]
            return paginator.get_paginated_response(serialized)

        return Response({
            'count': len(traces),
            'user_id': user_id_filter,
            'results': traces,
        })

    @action(detail=True, methods=['get'])
    def agents(self, request, pk=None):
        """
        Get agent decisions for a specific trace.

        Returns detailed information for each agent in the trace.
        """
        from data.stores import TraceStore
        store = TraceStore()
        trace = store.get_by_id(pk)

        if not trace:
            return Response({
                'status': 'error',
                'code': 'NOT_FOUND',
                'message': f'Trace {pk} not found',
            }, status=status.HTTP_404_NOT_FOUND)

        agents = trace.get('agents', [])
        return Response({
            'status': 'success',
            'trace_id': pk,
            'total_agents': len(agents),
            'agents': agents,
            '_links': {
                'self': f'/api/v1/traces/{pk}/agents/',
                'trace': f'/api/v1/traces/{pk}/',
            }
        })

    @action(detail=True, methods=['get'])
    def metrics(self, request, pk=None):
        """
        Get performance metrics for a trace.

        Includes timing information for each agent and overall pipeline.
        """
        from data.stores import TraceStore
        store = TraceStore()
        trace = store.get_by_id(pk)

        if not trace:
            return Response({
                'status': 'error',
                'code': 'NOT_FOUND',
                'message': f'Trace {pk} not found',
            }, status=status.HTTP_404_NOT_FOUND)

        agents = trace.get('agents', [])

        # Calculate metrics
        agent_metrics = []
        total_agent_time = 0

        for agent in agents:
            duration = agent.get('duration_ms', 0)
            total_agent_time += duration
            agent_metrics.append({
                'agent': agent.get('agent'),
                'duration_ms': duration,
                'status': agent.get('status'),
                'confidence': agent.get('confidence', 0),
            })

        total_duration = trace.get('total_duration_ms', 0)
        overhead = total_duration - total_agent_time

        return Response({
            'status': 'success',
            'trace_id': pk,
            'total_duration_ms': total_duration,
            'total_agent_time_ms': total_agent_time,
            'overhead_ms': overhead,
            'agents': agent_metrics,
            '_links': {
                'self': f'/api/v1/traces/{pk}/metrics/',
                'trace': f'/api/v1/traces/{pk}/',
            }
        })
