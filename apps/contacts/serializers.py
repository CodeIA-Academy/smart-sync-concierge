"""
Serializers for Contacts API.
Handles doctor, staff, and resource management.
"""

from rest_framework import serializers
from config.constants import CONTACT_TYPE_CHOICES
from config.validators import (
    validate_contact_id,
    validate_email,
    validate_phone_e164,
    validate_timezone,
)


class CoordinatesSerializer(serializers.Serializer):
    """Serializer for geographical coordinates."""

    lat = serializers.FloatField(min_value=-90, max_value=90)
    lng = serializers.FloatField(min_value=-180, max_value=180)


class ScheduleEntrySerializer(serializers.Serializer):
    """Serializer for individual schedule entry."""

    dia = serializers.IntegerField(min_value=1, max_value=7)  # 1=Monday, 7=Sunday
    hora_inicio = serializers.TimeField()
    hora_fin = serializers.TimeField()


class LocationHorarioSerializer(serializers.Serializer):
    """Serializer for working hours at a location."""

    lunes = ScheduleEntrySerializer(required=False)
    martes = ScheduleEntrySerializer(required=False)
    miercoles = ScheduleEntrySerializer(required=False)
    jueves = ScheduleEntrySerializer(required=False)
    viernes = ScheduleEntrySerializer(required=False)
    sabado = ScheduleEntrySerializer(required=False)
    domingo = ScheduleEntrySerializer(required=False)


class LocationSerializer(serializers.Serializer):
    """Serializer for contact location."""

    id = serializers.CharField(max_length=100)
    nombre = serializers.CharField(max_length=200)
    direccion = serializers.CharField(max_length=500)
    coordenadas = CoordinatesSerializer(required=False)
    timezone = serializers.CharField(
        validators=[validate_timezone],
        help_text="IANA timezone"
    )
    horario = LocationHorarioSerializer(required=False)
    disponible = serializers.BooleanField(default=True)


class ContactDetailSerializer(serializers.Serializer):
    """Complete contact serializer for read operations."""

    id = serializers.CharField(
        help_text="Unique contact ID"
    )
    nombre = serializers.CharField(
        max_length=255,
        help_text="Full name"
    )
    titulo = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Title or specialty"
    )
    tipo = serializers.ChoiceField(
        choices=['prestador', 'staff', 'resource'],
        help_text="Contact type: prestador, staff, or resource"
    )
    email = serializers.EmailField(
        required=False,
        allow_blank=True
    )
    telefono = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Phone number"
    )
    especialidades = serializers.ListField(
        required=False,
        help_text="List of specialties"
    )
    activo = serializers.BooleanField(
        default=True,
        help_text="Whether the contact is active"
    )
    created_at = serializers.DateTimeField(
        help_text="Creation timestamp"
    )
    updated_at = serializers.DateTimeField(
        help_text="Last update timestamp"
    )


class ContactCreateUpdateSerializer(serializers.Serializer):
    """Serializer for creating/updating contacts."""

    nombre = serializers.CharField(
        max_length=255,
        min_length=2
    )
    tipo = serializers.ChoiceField(
        choices=['prestador', 'staff', 'resource']
    )
    titulo = serializers.CharField(
        required=False,
        allow_blank=True
    )
    email = serializers.EmailField(required=False)
    telefono = serializers.CharField(
        required=False,
        allow_blank=True
    )
    especialidades = serializers.ListField(
        required=False,
        child=serializers.CharField(),
        allow_empty=True
    )
    activo = serializers.BooleanField(default=True)

    def validate_tipo(self, value):
        """Ensure type is one of the valid choices."""
        valid_types = ['prestador', 'staff', 'resource']
        if value not in valid_types:
            raise serializers.ValidationError(
                f"Tipo debe ser uno de: {', '.join(valid_types)}"
            )
        return value


class ContactListSerializer(serializers.Serializer):
    """Simplified serializer for contact list responses."""

    id = serializers.CharField()
    nombre = serializers.CharField()
    tipo = serializers.CharField()
    titulo = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    telefono = serializers.CharField(required=False)
    especialidades = serializers.ListField(required=False)
    activo = serializers.BooleanField()
    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)


class ContactAvailabilitySerializer(serializers.Serializer):
    """Serializer for contact availability check."""

    fecha = serializers.DateField()
    hora_inicio = serializers.TimeField()
    hora_fin = serializers.TimeField(required=False)
    ubicacion_id = serializers.CharField(
        required=False,
        help_text="Specific location to check"
    )


class ContactAvailabilityResponseSerializer(serializers.Serializer):
    """Serializer for availability response."""

    disponible = serializers.BooleanField()
    razon = serializers.CharField(
        required=False,
        help_text="Reason if not available"
    )
    slots_disponibles = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="Available time slots"
    )


class ContactSuccessResponseSerializer(serializers.Serializer):
    """Serializer for successful contact operations."""

    status = serializers.CharField(default='success')
    data = ContactDetailSerializer()
    message = serializers.CharField(help_text="User-friendly message")
    _links = serializers.DictField(
        required=False,
        help_text="HATEOAS links"
    )
