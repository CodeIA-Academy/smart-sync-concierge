"""Admin configuration for services app."""

from django.contrib import admin
from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'duracion_minutos', 'activo', 'created_at')
    list_filter = ('categoria', 'activo', 'created_at')
    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Información básica', {
            'fields': ('id', 'nombre', 'categoria', 'descripcion')
        }),
        ('Configuración', {
            'fields': ('duracion_minutos', 'activo')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
