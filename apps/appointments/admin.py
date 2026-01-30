"""Admin configuration for appointments app."""

from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'hora_inicio', 'status', 'usuario_id', 'created_at')
    list_filter = ('status', 'fecha', 'created_at')
    search_fields = ('id', 'usuario_id', 'prompt_original')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Información básica', {
            'fields': ('id', 'fecha', 'hora_inicio', 'hora_fin', 'duracion_minutos')
        }),
        ('Servicio y participantes', {
            'fields': ('tipo', 'participantes')
        }),
        ('Usuario y notas', {
            'fields': ('usuario_id', 'prompt_original', 'notas')
        }),
        ('Estado', {
            'fields': ('status',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'metadata'),
            'classes': ('collapse',)
        }),
    )
