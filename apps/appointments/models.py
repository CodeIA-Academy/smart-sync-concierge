"""
Appointments models.
Currently using JSON storage - models are placeholders for future database migration.
"""

# Placeholder for future models
# In v0.1.0 (MVP), we use JSON storage instead of database models
# In v0.3.0, these will be replaced with actual Django ORM models

"""
Future models:

from django.db import models
from django.contrib.auth.models import User

class Appointment(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    contact_id = models.CharField(max_length=100)
    service_id = models.CharField(max_length=100)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    status = models.CharField(max_length=20)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
"""
