"""
Appointments app configuration.
Handles appointment/cita management for Smart-Sync Concierge.
"""

from django.apps import AppConfig


class AppointmentsConfig(AppConfig):
    """Configuration for appointments app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.appointments'
    verbose_name = 'Appointments'

    def ready(self):
        """Initialize app when Django starts."""
        pass
