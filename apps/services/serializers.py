"""
Serializers for Services API.
Handles service/appointment type catalog management.
"""

from rest_framework import serializers
from config.constants import SERVICE_CATEGORY_CHOICES
from config.validators import (
    validate_service_id,
    validate_currency_code,
    validate_duration_minutes,
    validate_percentage,
    validate_price,
)


class RequirementsSerializer(serializers.Serializer):
    """Serializer for service requirements."""

    contacto_tipo = serializers.ChoiceField(
        choices=['doctor', 'staff', 'resource', 'cualquiera'],
        required=False
    )
    contacto_especialidad = serializers.CharField(required=False)
    ubicacion_tipo = serializers.ChoiceField(
        choices=['consultorio', 'sala', 'laboratorio', 'cualquiera'],
        required=False
    )
    equipos = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    preparacion_previa = serializers.BooleanField(default=False)
    instrucciones_preparacion = serializers.CharField(required=False)


class PrecioSerializer(serializers.Serializer):
    """Serializer for service pricing."""

    monto = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[validate_price]
    )
    moneda = serializers.CharField(
        max_length=3,
        validators=[validate_currency_code],
        default='MXN'
    )
    incluye = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    variables = serializers.BooleanField(default=False)
    factores_variacion = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class PenalitySerializer(serializers.Serializer):
    """Serializer for cancellation penalties."""

    tipo = serializers.ChoiceField(
        choices=['porcentaje', 'fijo', 'ninguna'],
        default='ninguna'
    )
    monto = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        validators=[validate_price]
    )
    porcentaje = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        validators=[validate_percentage]
    )


class PoliticasSerializer(serializers.Serializer):
    """Serializer for service policies."""

    cancelacion_anticipacion_horas = serializers.IntegerField(default=24)
    reprogramacion_anticipacion_horas = serializers.IntegerField(default=24)
    penalidad_cancelacion = PenalitySerializer(required=False)
    permite_urgencia = serializers.BooleanField(default=False)
    anticipacion_urgencia_minutos = serializers.IntegerField(required=False)


class DisponibilidadSerializer(serializers.Serializer):
    """Serializer for service availability configuration."""

    dias_anticipacion_maxima = serializers.IntegerField(default=90)
    minimo_anticipacion_horas = serializers.IntegerField(default=1)
    dias_no_permitidos = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=7),
        required=False
    )


class ReminderConfigSerializer(serializers.Serializer):
    """Serializer for reminder configuration."""

    minutos_antes = serializers.IntegerField(minimum=0)
    canales = serializers.ListField(
        child=serializers.ChoiceField(
            choices=['email', 'sms', 'whatsapp', 'push']
        )
    )


class RecordatoriosConfigSerializer(serializers.Serializer):
    """Serializer for appointment reminders configuration."""

    activo = serializers.BooleanField(default=True)
    recordatorios = ReminderConfigSerializer(many=True, required=False)


class MetadatosSerializer(serializers.Serializer):
    """Serializer for service metadata."""

    codigo_cie = serializers.CharField(required=False)
    requiere_autorizacion = serializers.BooleanField(required=False)
    frecuencia_recomendada = serializers.CharField(required=False)


class ServiceDetailSerializer(serializers.Serializer):
    """Complete service serializer for read operations."""

    id = serializers.CharField(
        validators=[validate_service_id],
        help_text="Unique service ID (service_xxxxx)"
    )
    nombre = serializers.CharField(
        max_length=100,
        min_length=2,
        help_text="Service name"
    )
    descripcion = serializers.CharField(
        required=False,
        max_length=500,
        help_text="Detailed description"
    )
    categoria = serializers.ChoiceField(
        choices=SERVICE_CATEGORY_CHOICES,
        help_text="Service category"
    )
    subcategoria = serializers.CharField(
        required=False,
        max_length=100,
        help_text="Specific subcategory"
    )
    duracion_minutos = serializers.IntegerField(
        validators=[validate_duration_minutes],
        help_text="Default duration in minutes"
    )
    duracion_minima_minutos = serializers.IntegerField(
        required=False,
        validators=[validate_duration_minutes]
    )
    duracion_maxima_minutos = serializers.IntegerField(
        required=False,
        validators=[validate_duration_minutes]
    )
    permite_sobrecupo = serializers.BooleanField(default=False)
    maximo_simultaneo = serializers.IntegerField(required=False)
    activo = serializers.BooleanField(default=True)
    requerimientos = RequirementsSerializer(required=False)
    precio = PrecioSerializer(required=False)
    politicas = PoliticasSerializer(required=False)
    disponibilidad = DisponibilidadSerializer(required=False)
    recordatorios_config = RecordatoriosConfigSerializer(required=False)
    metadatos = MetadatosSerializer(required=False)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField(required=False)


class ServiceCreateUpdateSerializer(serializers.Serializer):
    """Serializer for creating/updating services."""

    nombre = serializers.CharField(max_length=100, min_length=2)
    descripcion = serializers.CharField(
        required=False,
        max_length=500,
        allow_blank=True
    )
    categoria = serializers.ChoiceField(choices=SERVICE_CATEGORY_CHOICES)
    subcategoria = serializers.CharField(required=False, allow_blank=True)
    duracion_minutos = serializers.IntegerField(
        validators=[validate_duration_minutes]
    )
    duracion_minima_minutos = serializers.IntegerField(required=False)
    duracion_maxima_minutos = serializers.IntegerField(required=False)
    permite_sobrecupo = serializers.BooleanField(default=False)
    maximo_simultaneo = serializers.IntegerField(required=False)
    activo = serializers.BooleanField(default=True)
    requerimientos = RequirementsSerializer(required=False)
    precio = PrecioSerializer(required=False)
    politicas = PoliticasSerializer(required=False)
    disponibilidad = DisponibilidadSerializer(required=False)
    recordatorios_config = RecordatoriosConfigSerializer(required=False)
    metadatos = MetadatosSerializer(required=False)

    def validate(self, data):
        """Validate service configuration."""
        min_dur = data.get('duracion_minima_minutos')
        max_dur = data.get('duracion_maxima_minutos')
        default_dur = data.get('duracion_minutos')

        if min_dur and max_dur and min_dur >= max_dur:
            raise serializers.ValidationError({
                'duracion_maxima_minutos': 'Debe ser mayor que la duración mínima'
            })

        if min_dur and default_dur < min_dur:
            raise serializers.ValidationError({
                'duracion_minutos': 'Debe ser >= duración mínima'
            })

        if max_dur and default_dur > max_dur:
            raise serializers.ValidationError({
                'duracion_minutos': 'Debe ser <= duración máxima'
            })

        return data


class ServiceListSerializer(serializers.Serializer):
    """Simplified serializer for service list responses."""

    id = serializers.CharField()
    nombre = serializers.CharField()
    categoria = serializers.CharField()
    duracion_minutos = serializers.IntegerField()
    activo = serializers.BooleanField()
    precio = PrecioSerializer(required=False)


class ServiceSuccessResponseSerializer(serializers.Serializer):
    """Serializer for successful service operations."""

    status = serializers.CharField(default='success')
    data = ServiceDetailSerializer()
    message = serializers.CharField()
    _links = serializers.DictField(required=False)
