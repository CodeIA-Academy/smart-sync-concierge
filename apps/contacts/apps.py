"""
Contacts app configuration.
Handles contact management (doctors, staff, resources) for Smart-Sync Concierge.
"""

from django.apps import AppConfig


class ContactsConfig(AppConfig):
    """Configuration for contacts app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.contacts'
    verbose_name = 'Contacts'

    def ready(self):
        """Initialize app when Django starts."""
        pass
