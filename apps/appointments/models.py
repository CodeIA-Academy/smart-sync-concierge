"""
Appointments models for Smart-Sync Concierge.
"""

from django.db import models
from django.contrib.auth.models import User


class Appointment(models.Model):
    """Appointment model."""

    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmada'),
        ('cancelled', 'Cancelada'),
        ('completed', 'Completada'),
        ('no_show', 'No presentado'),
    ]

    id = models.CharField(max_length=100, primary_key=True)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    duracion_minutos = models.IntegerField(default=30)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tipo = models.JSONField(default=dict, help_text="Service type info: {id, nombre, categoria}")
    participantes = models.JSONField(default=list, help_text="Participants list")
    usuario_id = models.CharField(max_length=100, null=True, blank=True)
    prompt_original = models.TextField(null=True, blank=True)
    notas = models.JSONField(default=dict, help_text="Notes: {cliente, interna}")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha', '-hora_inicio']
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'

    def __str__(self):
        return f"Cita {self.id} - {self.fecha} {self.hora_inicio}"
