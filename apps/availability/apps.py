"""
Availability app configuration.
Handles availability queries and scheduling logic for Smart-Sync Concierge.
"""

from django.apps import AppConfig


class AvailabilityConfig(AppConfig):
    """Configuration for availability app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.availability'
    verbose_name = 'Availability'

    def ready(self):
        """Initialize app when Django starts."""
        pass
