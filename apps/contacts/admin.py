"""Admin configuration for contacts app."""

from django.contrib import admin
from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'email', 'telefono', 'activo', 'created_at')
    list_filter = ('tipo', 'activo', 'created_at')
    search_fields = ('nombre', 'email', 'telefono')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Información básica', {
            'fields': ('id', 'nombre', 'titulo', 'tipo')
        }),
        ('Contacto', {
            'fields': ('email', 'telefono')
        }),
        ('Especialidades', {
            'fields': ('especialidades',)
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
