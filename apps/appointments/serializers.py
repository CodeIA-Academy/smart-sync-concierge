"""
Serializers for Appointments API.
Handles request/response validation and transformation based on OpenAPI contracts.
"""

from rest_framework import serializers
from datetime import datetime, time
from config.constants import (
    APPOINTMENT_STATUS_CHOICES,
    APPOINTMENT_STATUS_PENDING,
)
from config.validators import (
    validate_appointment_id,
    validate_date_format,
    validate_time_format,
    validate_duration_minutes,
    validate_timezone,
)


class ParticipantContactSerializer(serializers.Serializer):
    """Serializer for participant contact information."""

    email = serializers.EmailField(required=False, allow_blank=True)
    telefono = serializers.CharField(required=False, allow_blank=True)


class ParticipantSerializer(serializers.Serializer):
    """Serializer for appointment participants."""

    id = serializers.CharField(max_length=100)
    nombre = serializers.CharField(max_length=200)
    rol = serializers.ChoiceField(choices=['prestador', 'cliente'])
    contacto = ParticipantContactSerializer(required=False)


class ServiceTypeSerializer(serializers.Serializer):
    """Serializer for service type reference."""

    id = serializers.CharField(max_length=100)
    nombre = serializers.CharField(max_length=200)
    categoria = serializers.ChoiceField(
        choices=['medica', 'odontologia', 'laboratorio', 'imagen', 'terapia', 'otra'],
        required=False
    )


class CoordinatesSerializer(serializers.Serializer):
    """Serializer for geographical coordinates."""

    lat = serializers.FloatField(min_value=-90, max_value=90)
    lng = serializers.FloatField(min_value=-180, max_value=180)


class LocationSerializer(serializers.Serializer):
    """Serializer for appointment location."""

    tipo = serializers.ChoiceField(
        choices=['presencial', 'virtual', 'domicilio'],
        required=False
    )
    direccion = serializers.CharField(required=False, allow_blank=True)
    coordenadas = CoordinatesSerializer(required=False)


class NotasSerializer(serializers.Serializer):
    """Serializer for appointment notes."""

    cliente = serializers.CharField(required=False, allow_blank=True)
    interna = serializers.CharField(required=False, allow_blank=True)
    ia_confidence = serializers.FloatField(
        min_value=0,
        max_value=1,
        required=False
    )


class ReminderSerializer(serializers.Serializer):
    """Serializer for appointment reminders."""

    tipo = serializers.ChoiceField(choices=['email', 'sms', 'push'])
    enviado = serializers.BooleanField(default=False)
    programado_para = serializers.DateTimeField(required=False)


class MetadataValidacionSerializer(serializers.Serializer):
    """Serializer for validation metadata."""

    contacto_validado = serializers.BooleanField(default=False)
    servicio_validado = serializers.BooleanField(default=False)
    horario_validado = serializers.BooleanField(default=False)
    conflictos_verificados = serializers.BooleanField(default=False)
    conflictos_encontrados = serializers.IntegerField(default=0)


class AppointmentDetailSerializer(serializers.Serializer):
    """
    Complete appointment serializer for read operations.
    Based on /docs/contracts/schemas/appointment.json
    """

    id = serializers.CharField(
        validators=[validate_appointment_id],
        help_text="Unique appointment ID (apt_YYYYMMDD_xxxxx)"
    )
    status = serializers.ChoiceField(
        choices=APPOINTMENT_STATUS_CHOICES,
        help_text="Appointment status"
    )
    created_at = serializers.DateTimeField(
        help_text="Creation timestamp (ISO 8601)"
    )
    updated_at = serializers.DateTimeField(
        required=False,
        help_text="Last update timestamp"
    )
    prompt_original = serializers.CharField(
        max_length=500,
        help_text="Original user prompt"
    )
    fecha = serializers.DateField(
        validators=[validate_date_format],
        help_text="Appointment date (YYYY-MM-DD)"
    )
    hora_inicio = serializers.TimeField(
        validators=[validate_time_format],
        help_text="Start time (HH:MM)"
    )
    hora_fin = serializers.TimeField(
        validators=[validate_time_format],
        help_text="End time (HH:MM)"
    )
    duracion_minutos = serializers.IntegerField(
        validators=[validate_duration_minutes],
        default=60,
        help_text="Duration in minutes (15-480)"
    )
    zona_horaria = serializers.CharField(
        validators=[validate_timezone],
        default='America/Mexico_City',
        help_text="Timezone (IANA format)"
    )
    tipo = ServiceTypeSerializer(
        help_text="Service type information"
    )
    participantes = ParticipantSerializer(
        many=True,
        help_text="List of appointment participants"
    )
    ubicacion = LocationSerializer(
        required=False,
        help_text="Appointment location"
    )
    notas = NotasSerializer(
        required=False,
        help_text="Appointment notes"
    )
    recordatorios = ReminderSerializer(
        many=True,
        required=False,
        help_text="Configured reminders"
    )
    metadata_validacion = MetadataValidacionSerializer(
        required=False,
        help_text="Validation metadata"
    )

    def validate_fecha(self, value):
        """Ensure appointment date is not in the past."""
        from django.utils import timezone
        if value < timezone.now().date():
            raise serializers.ValidationError(
                "La fecha de la cita no puede ser en el pasado"
            )
        return value

    def validate(self, data):
        """Validate that end time is after start time."""
        if data.get('hora_inicio') and data.get('hora_fin'):
            if data['hora_inicio'] >= data['hora_fin']:
                raise serializers.ValidationError({
                    'hora_fin': 'La hora de fin debe ser posterior a la hora de inicio'
                })
        return data


class AppointmentCreateSerializer(serializers.Serializer):
    """
    Simplified serializer for appointment creation from natural language.
    Used when user provides a prompt.
    """

    prompt = serializers.CharField(
        max_length=500,
        help_text="Natural language description of the appointment"
    )
    user_timezone = serializers.CharField(
        validators=[validate_timezone],
        default='America/Mexico_City',
        help_text="User's timezone for parsing"
    )
    user_id = serializers.CharField(
        max_length=100,
        required=False,
        help_text="User ID for reference"
    )


class AppointmentRescheduleSerializer(serializers.Serializer):
    """Serializer for rescheduling an appointment."""

    fecha = serializers.DateField(
        validators=[validate_date_format],
        help_text="New appointment date"
    )
    hora_inicio = serializers.TimeField(
        validators=[validate_time_format],
        help_text="New start time"
    )
    hora_fin = serializers.TimeField(
        validators=[validate_time_format],
        required=False,
        help_text="New end time (optional)"
    )
    notas = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Reason for rescheduling"
    )

    def validate_fecha(self, value):
        """Ensure new date is not in the past."""
        from django.utils import timezone
        if value < timezone.now().date():
            raise serializers.ValidationError(
                "La nueva fecha no puede ser en el pasado"
            )
        return value

    def validate(self, data):
        """Validate time range if end time is provided."""
        if data.get('hora_inicio') and data.get('hora_fin'):
            if data['hora_inicio'] >= data['hora_fin']:
                raise serializers.ValidationError({
                    'hora_fin': 'La hora de fin debe ser posterior a la hora de inicio'
                })
        return data


class AppointmentListSerializer(serializers.Serializer):
    """Simplified serializer for appointment list responses."""

    id = serializers.CharField()
    fecha = serializers.DateField()
    hora_inicio = serializers.TimeField()
    status = serializers.CharField()
    participantes = ParticipantSerializer(many=True)
    tipo = ServiceTypeSerializer()
    prompt_original = serializers.CharField()


class AppointmentConflictSerializer(serializers.Serializer):
    """Serializer for appointment conflict information."""

    type = serializers.CharField(
        help_text="Type of conflict (full_overlap, partial_overlap, etc.)"
    )
    existing_appointment_id = serializers.CharField(
        required=False,
        help_text="ID of conflicting appointment"
    )
    message = serializers.CharField(
        help_text="Human-readable conflict description"
    )


class SuggestionSerializer(serializers.Serializer):
    """Serializer for alternative appointment suggestions."""

    fecha = serializers.DateField(
        help_text="Suggested date"
    )
    hora_inicio = serializers.TimeField(
        help_text="Suggested start time"
    )
    hora_fin = serializers.TimeField(
        required=False,
        help_text="Suggested end time"
    )
    confidence = serializers.FloatField(
        min_value=0,
        max_value=1,
        help_text="Confidence score for suggestion (0-1)"
    )
    reason = serializers.CharField(
        help_text="Reason why this time is suggested"
    )


class AppointmentSuccessResponseSerializer(serializers.Serializer):
    """Serializer for successful appointment operations."""

    status = serializers.CharField(default='success')
    data = AppointmentDetailSerializer()
    message = serializers.CharField(help_text="User-friendly message")
    _links = serializers.DictField(
        child=serializers.CharField(),
        required=False,
        help_text="HATEOAS links for navigation"
    )


class AppointmentConflictResponseSerializer(serializers.Serializer):
    """Serializer for conflict responses (HTTP 409)."""

    status = serializers.CharField(default='error')
    code = serializers.CharField(default='CONFLICT')
    message = serializers.CharField()
    details = AppointmentConflictSerializer()
    suggestions = SuggestionSerializer(
        many=True,
        help_text="Alternative appointment suggestions"
    )


class AppointmentInvalidResponseSerializer(serializers.Serializer):
    """Serializer for invalid/ambiguous prompt responses (HTTP 400)."""

    status = serializers.CharField(default='error')
    code = serializers.CharField(default='INSUFFICIENT_INFO')
    message = serializers.CharField()
    ambiguities = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of ambiguous fields"
    )
