"""
Project-wide constants and enums for Smart-Sync Concierge.
Centralizes all constant values used throughout the application.
"""

# ============================================================================
# APPOINTMENT STATUS
# ============================================================================

APPOINTMENT_STATUS_PENDING = 'pending'
APPOINTMENT_STATUS_CONFIRMED = 'confirmed'
APPOINTMENT_STATUS_RESCHEDULED = 'rescheduled'
APPOINTMENT_STATUS_CANCELLED = 'cancelled'
APPOINTMENT_STATUS_COMPLETED = 'completed'
APPOINTMENT_STATUS_NO_SHOW = 'no_show'

APPOINTMENT_STATUSES = {
    APPOINTMENT_STATUS_PENDING: 'Pendiente',
    APPOINTMENT_STATUS_CONFIRMED: 'Confirmada',
    APPOINTMENT_STATUS_RESCHEDULED: 'Reprogramada',
    APPOINTMENT_STATUS_CANCELLED: 'Cancelada',
    APPOINTMENT_STATUS_COMPLETED: 'Completada',
    APPOINTMENT_STATUS_NO_SHOW: 'No presentado',
}

APPOINTMENT_STATUS_CHOICES = [
    (APPOINTMENT_STATUS_PENDING, APPOINTMENT_STATUSES[APPOINTMENT_STATUS_PENDING]),
    (APPOINTMENT_STATUS_CONFIRMED, APPOINTMENT_STATUSES[APPOINTMENT_STATUS_CONFIRMED]),
    (APPOINTMENT_STATUS_RESCHEDULED, APPOINTMENT_STATUSES[APPOINTMENT_STATUS_RESCHEDULED]),
    (APPOINTMENT_STATUS_CANCELLED, APPOINTMENT_STATUSES[APPOINTMENT_STATUS_CANCELLED]),
    (APPOINTMENT_STATUS_COMPLETED, APPOINTMENT_STATUSES[APPOINTMENT_STATUS_COMPLETED]),
    (APPOINTMENT_STATUS_NO_SHOW, APPOINTMENT_STATUSES[APPOINTMENT_STATUS_NO_SHOW]),
]

# ============================================================================
# CONTACT TYPES
# ============================================================================

CONTACT_TYPE_DOCTOR = 'doctor'
CONTACT_TYPE_STAFF = 'staff'
CONTACT_TYPE_RESOURCE = 'resource'

CONTACT_TYPES = {
    CONTACT_TYPE_DOCTOR: 'Doctor',
    CONTACT_TYPE_STAFF: 'Staff',
    CONTACT_TYPE_RESOURCE: 'Recurso',
}

CONTACT_TYPE_CHOICES = [
    (CONTACT_TYPE_DOCTOR, CONTACT_TYPES[CONTACT_TYPE_DOCTOR]),
    (CONTACT_TYPE_STAFF, CONTACT_TYPES[CONTACT_TYPE_STAFF]),
    (CONTACT_TYPE_RESOURCE, CONTACT_TYPES[CONTACT_TYPE_RESOURCE]),
]

# ============================================================================
# SERVICE CATEGORIES
# ============================================================================

SERVICE_CATEGORY_MEDICA = 'medica'
SERVICE_CATEGORY_ODONTOLOGIA = 'odontologia'
SERVICE_CATEGORY_LABORATORIO = 'laboratorio'
SERVICE_CATEGORY_IMAGEN = 'imagen'
SERVICE_CATEGORY_TERAPIA = 'terapia'
SERVICE_CATEGORY_OTRA = 'otra'

SERVICE_CATEGORIES = {
    SERVICE_CATEGORY_MEDICA: 'Médica',
    SERVICE_CATEGORY_ODONTOLOGIA: 'Odontología',
    SERVICE_CATEGORY_LABORATORIO: 'Laboratorio',
    SERVICE_CATEGORY_IMAGEN: 'Imagen',
    SERVICE_CATEGORY_TERAPIA: 'Terapia',
    SERVICE_CATEGORY_OTRA: 'Otra',
}

SERVICE_CATEGORY_CHOICES = [
    (SERVICE_CATEGORY_MEDICA, SERVICE_CATEGORIES[SERVICE_CATEGORY_MEDICA]),
    (SERVICE_CATEGORY_ODONTOLOGIA, SERVICE_CATEGORIES[SERVICE_CATEGORY_ODONTOLOGIA]),
    (SERVICE_CATEGORY_LABORATORIO, SERVICE_CATEGORIES[SERVICE_CATEGORY_LABORATORIO]),
    (SERVICE_CATEGORY_IMAGEN, SERVICE_CATEGORIES[SERVICE_CATEGORY_IMAGEN]),
    (SERVICE_CATEGORY_TERAPIA, SERVICE_CATEGORIES[SERVICE_CATEGORY_TERAPIA]),
    (SERVICE_CATEGORY_OTRA, SERVICE_CATEGORIES[SERVICE_CATEGORY_OTRA]),
]

# ============================================================================
# LOCATION TYPES
# ============================================================================

LOCATION_TYPE_CONSULTORIO = 'consultorio'
LOCATION_TYPE_SALA = 'sala'
LOCATION_TYPE_LABORATORIO = 'laboratorio'
LOCATION_TYPE_CUALQUIERA = 'cualquiera'

LOCATION_TYPES = {
    LOCATION_TYPE_CONSULTORIO: 'Consultorio',
    LOCATION_TYPE_SALA: 'Sala',
    LOCATION_TYPE_LABORATORIO: 'Laboratorio',
    LOCATION_TYPE_CUALQUIERA: 'Cualquiera',
}

LOCATION_TYPE_CHOICES = [
    (LOCATION_TYPE_CONSULTORIO, LOCATION_TYPES[LOCATION_TYPE_CONSULTORIO]),
    (LOCATION_TYPE_SALA, LOCATION_TYPES[LOCATION_TYPE_SALA]),
    (LOCATION_TYPE_LABORATORIO, LOCATION_TYPES[LOCATION_TYPE_LABORATORIO]),
    (LOCATION_TYPE_CUALQUIERA, LOCATION_TYPES[LOCATION_TYPE_CUALQUIERA]),
]

# ============================================================================
# NOTIFICATION CHANNELS
# ============================================================================

NOTIFICATION_CHANNEL_EMAIL = 'email'
NOTIFICATION_CHANNEL_SMS = 'sms'
NOTIFICATION_CHANNEL_WHATSAPP = 'whatsapp'
NOTIFICATION_CHANNEL_PUSH = 'push'

NOTIFICATION_CHANNELS = {
    NOTIFICATION_CHANNEL_EMAIL: 'Email',
    NOTIFICATION_CHANNEL_SMS: 'SMS',
    NOTIFICATION_CHANNEL_WHATSAPP: 'WhatsApp',
    NOTIFICATION_CHANNEL_PUSH: 'Push Notification',
}

NOTIFICATION_CHANNEL_CHOICES = [
    (NOTIFICATION_CHANNEL_EMAIL, NOTIFICATION_CHANNELS[NOTIFICATION_CHANNEL_EMAIL]),
    (NOTIFICATION_CHANNEL_SMS, NOTIFICATION_CHANNELS[NOTIFICATION_CHANNEL_SMS]),
    (NOTIFICATION_CHANNEL_WHATSAPP, NOTIFICATION_CHANNELS[NOTIFICATION_CHANNEL_WHATSAPP]),
    (NOTIFICATION_CHANNEL_PUSH, NOTIFICATION_CHANNELS[NOTIFICATION_CHANNEL_PUSH]),
]

# ============================================================================
# CANCELLATION PENALTY TYPES
# ============================================================================

PENALTY_TYPE_PORCENTAJE = 'porcentaje'
PENALTY_TYPE_FIJO = 'fijo'
PENALTY_TYPE_NINGUNA = 'ninguna'

PENALTY_TYPES = {
    PENALTY_TYPE_PORCENTAJE: 'Porcentaje',
    PENALTY_TYPE_FIJO: 'Monto Fijo',
    PENALTY_TYPE_NINGUNA: 'Ninguna',
}

PENALTY_TYPE_CHOICES = [
    (PENALTY_TYPE_PORCENTAJE, PENALTY_TYPES[PENALTY_TYPE_PORCENTAJE]),
    (PENALTY_TYPE_FIJO, PENALTY_TYPES[PENALTY_TYPE_FIJO]),
    (PENALTY_TYPE_NINGUNA, PENALTY_TYPES[PENALTY_TYPE_NINGUNA]),
]

# ============================================================================
# CONFLICT TYPES
# ============================================================================

CONFLICT_TYPE_FULL_OVERLAP = 'full_overlap'
CONFLICT_TYPE_PARTIAL_OVERLAP = 'partial_overlap'
CONFLICT_TYPE_BUFFER_VIOLATION = 'buffer_violation'
CONFLICT_TYPE_UNAVAILABLE_LOCATION = 'unavailable_location'
CONFLICT_TYPE_UNAVAILABLE_CONTACT = 'unavailable_contact'
CONFLICT_TYPE_INVALID_HOURS = 'invalid_hours'

CONFLICT_TYPES = {
    CONFLICT_TYPE_FULL_OVERLAP: 'Solapamiento Completo',
    CONFLICT_TYPE_PARTIAL_OVERLAP: 'Solapamiento Parcial',
    CONFLICT_TYPE_BUFFER_VIOLATION: 'Violación de Buffer',
    CONFLICT_TYPE_UNAVAILABLE_LOCATION: 'Ubicación No Disponible',
    CONFLICT_TYPE_UNAVAILABLE_CONTACT: 'Contacto No Disponible',
    CONFLICT_TYPE_INVALID_HOURS: 'Horas No Permitidas',
}

# ============================================================================
# ERROR CODES
# ============================================================================

ERROR_CODE_INVALID_REQUEST = 'INVALID_REQUEST'
ERROR_CODE_INSUFFICIENT_INFO = 'INSUFFICIENT_INFO'
ERROR_CODE_CONFLICT = 'CONFLICT'
ERROR_CODE_NOT_FOUND = 'NOT_FOUND'
ERROR_CODE_UNAUTHORIZED = 'UNAUTHORIZED'
ERROR_CODE_FORBIDDEN = 'FORBIDDEN'
ERROR_CODE_INTERNAL_ERROR = 'INTERNAL_ERROR'
ERROR_CODE_SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE'

# ============================================================================
# DAYS OF WEEK
# ============================================================================

DAY_MONDAY = 1
DAY_TUESDAY = 2
DAY_WEDNESDAY = 3
DAY_THURSDAY = 4
DAY_FRIDAY = 5
DAY_SATURDAY = 6
DAY_SUNDAY = 7

DAYS_OF_WEEK = {
    DAY_MONDAY: 'Lunes',
    DAY_TUESDAY: 'Martes',
    DAY_WEDNESDAY: 'Miércoles',
    DAY_THURSDAY: 'Jueves',
    DAY_FRIDAY: 'Viernes',
    DAY_SATURDAY: 'Sábado',
    DAY_SUNDAY: 'Domingo',
}

DAYS_OF_WEEK_CHOICES = [
    (DAY_MONDAY, DAYS_OF_WEEK[DAY_MONDAY]),
    (DAY_TUESDAY, DAYS_OF_WEEK[DAY_TUESDAY]),
    (DAY_WEDNESDAY, DAYS_OF_WEEK[DAY_WEDNESDAY]),
    (DAY_THURSDAY, DAYS_OF_WEEK[DAY_THURSDAY]),
    (DAY_FRIDAY, DAYS_OF_WEEK[DAY_FRIDAY]),
    (DAY_SATURDAY, DAYS_OF_WEEK[DAY_SATURDAY]),
    (DAY_SUNDAY, DAYS_OF_WEEK[DAY_SUNDAY]),
]

# Default working days (Monday to Friday)
DEFAULT_WORKING_DAYS = [DAY_MONDAY, DAY_TUESDAY, DAY_WEDNESDAY, DAY_THURSDAY, DAY_FRIDAY]

# ============================================================================
# CURRENCY CODES
# ============================================================================

CURRENCY_MXN = 'MXN'
CURRENCY_USD = 'USD'
CURRENCY_EUR = 'EUR'

CURRENCIES = {
    CURRENCY_MXN: 'Mexican Peso',
    CURRENCY_USD: 'US Dollar',
    CURRENCY_EUR: 'Euro',
}

DEFAULT_CURRENCY = CURRENCY_MXN

# ============================================================================
# ID PREFIXES (For semantic identification)
# ============================================================================

ID_PREFIX_APPOINTMENT = 'apt_'
ID_PREFIX_CONTACT = 'contact_'
ID_PREFIX_SERVICE = 'service_'
ID_PREFIX_LOCATION = 'loc_'
ID_PREFIX_SCHEDULE = 'sch_'

# ============================================================================
# TIME CONSTRAINTS
# ============================================================================

# Default appointment duration (in minutes)
DEFAULT_APPOINTMENT_DURATION = 60
MIN_APPOINTMENT_DURATION = 15
MAX_APPOINTMENT_DURATION = 480  # 8 hours

# Default buffer between appointments (in minutes)
DEFAULT_BUFFER_MINUTES = 5

# Minimum hours in advance to book
DEFAULT_MIN_HOURS_IN_ADVANCE = 1

# Maximum days in advance to book
DEFAULT_MAX_DAYS_IN_ADVANCE = 90

# Default working hours
DEFAULT_WORKING_HOURS_START = 8  # 8:00 AM
DEFAULT_WORKING_HOURS_END = 18   # 6:00 PM

# ============================================================================
# REGEX PATTERNS
# ============================================================================

# ID patterns
PATTERN_APPOINTMENT_ID = r'^apt_[0-9]{8}_[a-z0-9]+$'
PATTERN_CONTACT_ID = r'^contact_[a-z0-9_]+$'
PATTERN_SERVICE_ID = r'^service_[a-z0-9_]+$'

# Phone pattern (E.164 format)
PATTERN_PHONE_E164 = r'^\+[1-9]\d{1,14}$'

# Email pattern
PATTERN_EMAIL = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# Date pattern (YYYY-MM-DD)
PATTERN_DATE = r'^\d{4}-\d{2}-\d{2}$'

# Time pattern (HH:MM)
PATTERN_TIME = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'

# ============================================================================
# RESPONSE MESSAGES
# ============================================================================

MESSAGE_SUCCESS = 'Operación exitosa'
MESSAGE_CREATED = 'Recurso creado exitosamente'
MESSAGE_UPDATED = 'Recurso actualizado exitosamente'
MESSAGE_DELETED = 'Recurso eliminado exitosamente'
MESSAGE_NOT_FOUND = 'Recurso no encontrado'
MESSAGE_CONFLICT = 'Conflicto: El horario no está disponible'
MESSAGE_UNAUTHORIZED = 'No autorizado'
MESSAGE_FORBIDDEN = 'Acceso prohibido'
MESSAGE_INVALID_REQUEST = 'Solicitud inválida'

# ============================================================================
# METADATA
# ============================================================================

API_VERSION = '0.1.0'
API_TITLE = 'Smart-Sync Concierge API'
API_DESCRIPTION = 'API para gestión inteligente de citas médicas'
