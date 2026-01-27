"""
Custom validators for Smart-Sync Concierge API.
Provides validation functions for common data types and formats.
"""

import re
from datetime import datetime, time
from django.core.exceptions import ValidationError
from rest_framework import serializers
from .constants import (
    PATTERN_APPOINTMENT_ID,
    PATTERN_CONTACT_ID,
    PATTERN_SERVICE_ID,
    PATTERN_PHONE_E164,
    PATTERN_EMAIL,
    PATTERN_DATE,
    PATTERN_TIME,
    MIN_APPOINTMENT_DURATION,
    MAX_APPOINTMENT_DURATION,
)


# ============================================================================
# ID VALIDATORS
# ============================================================================

def validate_appointment_id(value):
    """Validate appointment ID format (apt_YYYYMMDD_[a-z0-9]+)."""
    if not re.match(PATTERN_APPOINTMENT_ID, value):
        raise serializers.ValidationError(
            f"ID de cita inválido. Debe tener el formato: apt_YYYYMMDD_xxxxx"
        )
    return value


def validate_contact_id(value):
    """Validate contact ID format (contact_[a-z0-9_]+)."""
    if not re.match(PATTERN_CONTACT_ID, value):
        raise serializers.ValidationError(
            f"ID de contacto inválido. Debe tener el formato: contact_xxxxx"
        )
    return value


def validate_service_id(value):
    """Validate service ID format (service_[a-z0-9_]+)."""
    if not re.match(PATTERN_SERVICE_ID, value):
        raise serializers.ValidationError(
            f"ID de servicio inválido. Debe tener el formato: service_xxxxx"
        )
    return value


# ============================================================================
# CONTACT VALIDATORS
# ============================================================================

def validate_phone_e164(value):
    """Validate phone number in E.164 format (+525512345678)."""
    if not re.match(PATTERN_PHONE_E164, value):
        raise serializers.ValidationError(
            f"Número de teléfono inválido. Debe estar en formato E.164 (+525512345678)"
        )
    return value


def validate_email(value):
    """Validate email format."""
    if not re.match(PATTERN_EMAIL, value):
        raise serializers.ValidationError(
            f"Correo electrónico inválido: {value}"
        )
    return value


# ============================================================================
# DATE & TIME VALIDATORS
# ============================================================================

def validate_date_format(value):
    """Validate date format (YYYY-MM-DD)."""
    if not re.match(PATTERN_DATE, value):
        raise serializers.ValidationError(
            f"Formato de fecha inválido. Debe ser YYYY-MM-DD"
        )
    try:
        datetime.strptime(value, '%Y-%m-%d')
    except ValueError:
        raise serializers.ValidationError(
            f"Fecha inválida: {value}"
        )
    return value


def validate_time_format(value):
    """Validate time format (HH:MM)."""
    if not re.match(PATTERN_TIME, value):
        raise serializers.ValidationError(
            f"Formato de hora inválido. Debe ser HH:MM (24h)"
        )
    try:
        datetime.strptime(value, '%H:%M').time()
    except ValueError:
        raise serializers.ValidationError(
            f"Hora inválida: {value}"
        )
    return value


def validate_future_date(value):
    """Validate that date is in the future."""
    validate_date_format(value)
    date_obj = datetime.strptime(value, '%Y-%m-%d').date()
    from django.utils import timezone
    if date_obj <= timezone.now().date():
        raise serializers.ValidationError(
            "La fecha debe ser en el futuro"
        )
    return value


def validate_time_range(start_time, end_time):
    """Validate that start_time < end_time."""
    try:
        start = datetime.strptime(start_time, '%H:%M').time()
        end = datetime.strptime(end_time, '%H:%M').time()
        if start >= end:
            raise serializers.ValidationError(
                "La hora de inicio debe ser anterior a la hora de fin"
            )
    except ValueError:
        raise serializers.ValidationError(
            "Formato de hora inválido"
        )
    return True


# ============================================================================
# APPOINTMENT VALIDATORS
# ============================================================================

def validate_duration_minutes(value):
    """Validate appointment duration is within allowed range."""
    if value < MIN_APPOINTMENT_DURATION or value > MAX_APPOINTMENT_DURATION:
        raise serializers.ValidationError(
            f"Duración debe estar entre {MIN_APPOINTMENT_DURATION} y {MAX_APPOINTMENT_DURATION} minutos"
        )
    return value


def validate_min_max_duration(min_duration, max_duration):
    """Validate that min_duration < max_duration."""
    if min_duration >= max_duration:
        raise serializers.ValidationError(
            "La duración mínima debe ser menor que la duración máxima"
        )
    return True


# ============================================================================
# NUMERIC VALIDATORS
# ============================================================================

def validate_positive_number(value):
    """Validate that number is positive."""
    if value <= 0:
        raise serializers.ValidationError(
            "El valor debe ser positivo"
        )
    return value


def validate_percentage(value):
    """Validate that value is a valid percentage (0-100)."""
    if value < 0 or value > 100:
        raise serializers.ValidationError(
            "El porcentaje debe estar entre 0 y 100"
        )
    return value


def validate_price(value):
    """Validate price format."""
    if value < 0:
        raise serializers.ValidationError(
            "El precio no puede ser negativo"
        )
    # Check for maximum 2 decimal places
    if isinstance(value, float):
        if len(str(value).split('.')[-1]) > 2:
            raise serializers.ValidationError(
                "El precio puede tener máximo 2 decimales"
            )
    return value


# ============================================================================
# STRING VALIDATORS
# ============================================================================

def validate_non_empty_string(value):
    """Validate that string is not empty."""
    if not value or not value.strip():
        raise serializers.ValidationError(
            "Este campo no puede estar vacío"
        )
    return value


def validate_string_length(value, min_length=None, max_length=None):
    """Validate string length."""
    if min_length and len(value) < min_length:
        raise serializers.ValidationError(
            f"La longitud mínima es {min_length} caracteres"
        )
    if max_length and len(value) > max_length:
        raise serializers.ValidationError(
            f"La longitud máxima es {max_length} caracteres"
        )
    return value


# ============================================================================
# CURRENCY VALIDATORS
# ============================================================================

def validate_currency_code(value):
    """Validate ISO 4217 currency code format."""
    if not re.match(r'^[A-Z]{3}$', value):
        raise serializers.ValidationError(
            f"Código de moneda inválido. Debe ser un código ISO 4217 (ej: MXN, USD)"
        )
    return value


# ============================================================================
# LIST VALIDATORS
# ============================================================================

def validate_list_not_empty(value):
    """Validate that list is not empty."""
    if not isinstance(value, list) or len(value) == 0:
        raise serializers.ValidationError(
            "Esta lista no puede estar vacía"
        )
    return value


def validate_unique_list_items(value):
    """Validate that list items are unique."""
    if len(value) != len(set(value)):
        raise serializers.ValidationError(
            "La lista contiene elementos duplicados"
        )
    return value


# ============================================================================
# TIMEZONE VALIDATORS
# ============================================================================

def validate_timezone(value):
    """Validate IANA timezone format."""
    try:
        from zoneinfo import ZoneInfo
        ZoneInfo(value)
    except Exception:
        raise serializers.ValidationError(
            f"Zona horaria inválida: {value}. Debe ser una zona horaria IANA válida"
        )
    return value


# ============================================================================
# JSON VALIDATORS
# ============================================================================

def validate_json_structure(value, required_keys=None):
    """Validate JSON structure has required keys."""
    if not isinstance(value, dict):
        raise serializers.ValidationError(
            "El valor debe ser un objeto JSON válido"
        )
    if required_keys:
        missing_keys = set(required_keys) - set(value.keys())
        if missing_keys:
            raise serializers.ValidationError(
                f"Campos requeridos faltantes: {', '.join(missing_keys)}"
            )
    return value
