"""
Services models for Smart-Sync Concierge.
"""

from django.db import models


class Service(models.Model):
    """Service/appointment type catalog model."""

    CATEGORY_CHOICES = [
        ('medica', 'Médica'),
        ('administrativa', 'Administrativa'),
        ('mantenimiento', 'Mantenimiento'),
        ('otro', 'Otro'),
    ]

    id = models.CharField(max_length=100, primary_key=True)
    nombre = models.CharField(max_length=255)
    categoria = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='medica')
    descripcion = models.TextField(null=True, blank=True)
    duracion_minutos = models.IntegerField(default=30)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'

    def __str__(self):
        return self.nombre
