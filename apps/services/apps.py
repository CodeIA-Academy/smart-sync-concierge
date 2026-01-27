"""
Services app configuration.
Handles service/appointment type catalog for Smart-Sync Concierge.
"""

from django.apps import AppConfig


class ServicesConfig(AppConfig):
    """Configuration for services app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.services'
    verbose_name = 'Services'

    def ready(self):
        """Initialize app when Django starts."""
        pass
