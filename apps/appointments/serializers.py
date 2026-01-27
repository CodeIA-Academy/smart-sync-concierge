"""
Serializers for appointments API.
Used for request/response validation and transformation.
"""

from rest_framework import serializers

# Placeholder for future serializers
# These will be implemented based on the JSON schemas in /docs/contracts/schemas/

"""
Example future implementation:

from config.constants import APPOINTMENT_STATUSES
from config.validators import validate_appointment_id, validate_date_format

class AppointmentSerializer(serializers.Serializer):
    id = serializers.CharField(validators=[validate_appointment_id])
    contact_id = serializers.CharField()
    service_id = serializers.CharField()
    fecha = serializers.CharField(validators=[validate_date_format])
    hora_inicio = serializers.TimeField()
    hora_fin = serializers.TimeField()
    status = serializers.ChoiceField(choices=APPOINTMENT_STATUSES.keys())
    metadata = serializers.JSONField()
"""
