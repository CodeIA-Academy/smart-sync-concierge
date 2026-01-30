"""
Contacts models for Smart-Sync Concierge.
"""

from django.db import models


class Contact(models.Model):
    """Contact model for doctors, staff, and resources."""

    TYPE_CHOICES = [
        ('prestador', 'Prestador de Servicios'),
        ('staff', 'Personal'),
        ('resource', 'Recurso'),
    ]

    id = models.CharField(max_length=100, primary_key=True)
    nombre = models.CharField(max_length=255)
    titulo = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TYPE_CHOICES, default='prestador')
    especialidades = models.JSONField(default=list, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Contacto'
        verbose_name_plural = 'Contactos'

    def __str__(self):
        return self.nombre
