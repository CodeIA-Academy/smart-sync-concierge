"""
ValidationAgent - Validates extracted and resolved data integrity.

Responsible for:
- Validating ID formats (contact_id, service_id)
- Validating date formats (YYYY-MM-DD)
- Validating time formats (HH:MM)
- Verifying entities exist in system
- Checking duration constraints
"""

import re
from typing import Any, Dict, List, Optional
import time

from .base import BaseAgent, AgentResult


class ValidationAgent(BaseAgent):
    """Validates data integrity and format."""

    def __init__(self):
        """Initialize ValidationAgent."""
        super().__init__("validation", version="1.0.0")

        # Regex patterns for validation
        self.patterns = {
            "date": r"^\d{4}-\d{2}-\d{2}$",  # YYYY-MM-DD
            "time": r"^\d{2}:\d{2}$",  # HH:MM
            "id": r"^[a-z_]+_[a-zA-Z0-9_]+$",  # semantic_id format
            "contact_id": r"^contact_",
            "service_id": r"^service_",
        }

    def run(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Validate appointment data.

        Args:
            input_data: {
                "contacto_id": str (optional),
                "contacto_nombre": str (optional),
                "fecha": str (YYYY-MM-DD),
                "hora_inicio": str (HH:MM),
                "hora_fin": str (HH:MM),
                "ubicacion_id": str (optional),
                "servicio_id": str (optional),
                "stores": dict (AppointmentStore, ContactStore, ServiceStore)
            }

        Returns:
            AgentResult with validation status and errors
        """
        start_time = time.time()

        try:
            errors = []
            warnings = []
            validated_data = {}

            # Validate required fields
            fecha = input_data.get("fecha")
            hora_inicio = input_data.get("hora_inicio")
            hora_fin = input_data.get("hora_fin")

            # Validate date format
            if not fecha:
                errors.append("Missing required field: fecha")
            elif not self._validate_format("date", fecha):
                errors.append(f"Invalid date format: {fecha} (expected YYYY-MM-DD)")
            else:
                validated_data["fecha"] = fecha

            # Validate time format
            if not hora_inicio:
                errors.append("Missing required field: hora_inicio")
            elif not self._validate_format("time", hora_inicio):
                errors.append(f"Invalid time format: {hora_inicio} (expected HH:MM)")
            else:
                validated_data["hora_inicio"] = hora_inicio

            if not hora_fin:
                errors.append("Missing required field: hora_fin")
            elif not self._validate_format("time", hora_fin):
                errors.append(f"Invalid time format: {hora_fin} (expected HH:MM)")
            else:
                validated_data["hora_fin"] = hora_fin

            # Validate time logic (start < end)
            if hora_inicio and hora_fin:
                if not self._validate_time_range(hora_inicio, hora_fin):
                    errors.append(f"Invalid time range: {hora_inicio} must be before {hora_fin}")

            # Validate contact
            contacto_id = input_data.get("contacto_id")
            contacto_nombre = input_data.get("contacto_nombre")

            if contacto_id and not self._validate_format("id", contacto_id):
                warnings.append(f"Contact ID format looks unusual: {contacto_id}")
            elif contacto_id:
                validated_data["contacto_id"] = contacto_id

            if contacto_nombre:
                validated_data["contacto_nombre"] = contacto_nombre

            # Validate location (optional)
            ubicacion_id = input_data.get("ubicacion_id")
            if ubicacion_id and not self._validate_format("id", ubicacion_id):
                warnings.append(f"Location ID format looks unusual: {ubicacion_id}")
            elif ubicacion_id:
                validated_data["ubicacion_id"] = ubicacion_id

            # Validate service (optional)
            servicio_id = input_data.get("servicio_id")
            if servicio_id and not self._validate_format("id", servicio_id):
                warnings.append(f"Service ID format looks unusual: {servicio_id}")
            elif servicio_id:
                validated_data["servicio_id"] = servicio_id

            # Verify entities exist (if stores provided)
            stores = input_data.get("stores", {})
            if stores:
                contact_store = stores.get("contact_store")
                service_store = stores.get("service_store")

                # Verify contact exists
                if contacto_id and contact_store:
                    contact = contact_store.get_by_id(contacto_id)
                    if not contact:
                        errors.append(f"Contact not found: {contacto_id}")
                    elif not contact.get("activo", True):
                        errors.append(f"Contact is inactive: {contacto_id}")

                # Verify service exists
                if servicio_id and service_store:
                    service = service_store.get_by_id(servicio_id)
                    if not service:
                        errors.append(f"Service not found: {servicio_id}")
                    elif not service.get("activo", True):
                        errors.append(f"Service is inactive: {servicio_id}")

                # Verify location exists for contact
                if contacto_id and ubicacion_id and contact_store:
                    contact = contact_store.get_by_id(contacto_id)
                    if contact:
                        locations = contact.get("ubicaciones", [])
                        location_ids = [loc.get("id") for loc in locations]
                        if ubicacion_id not in location_ids:
                            errors.append(f"Location {ubicacion_id} not found for contact {contacto_id}")

            duration_ms = int((time.time() - start_time) * 1000)

            # Return result based on validation
            if errors:
                return self._error(
                    f"Validation failed with {len(errors)} error(s)",
                    errors=errors,
                    duration_ms=duration_ms,
                )

            if warnings:
                return self._warning(
                    validated_data,
                    f"Validation succeeded with {len(warnings)} warning(s)",
                    warnings=warnings,
                    confidence=0.85,
                    duration_ms=duration_ms,
                )

            return self._success(
                validated_data,
                "All validations passed",
                confidence=0.95,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_debug(f"ValidationAgent error: {str(e)}")
            return self._error(f"Validation error: {str(e)}", duration_ms=duration_ms)

    def _validate_format(self, field_type: str, value: str) -> bool:
        """
        Validate field format using regex patterns.

        Args:
            field_type: Type of field (date, time, id, etc.)
            value: Value to validate

        Returns:
            True if valid, False otherwise
        """
        if field_type not in self.patterns:
            return True

        pattern = self.patterns[field_type]
        return bool(re.match(pattern, value))

    def _validate_time_range(self, hora_inicio: str, hora_fin: str) -> bool:
        """
        Validate that start time is before end time.

        Args:
            hora_inicio: Start time (HH:MM)
            hora_fin: End time (HH:MM)

        Returns:
            True if start < end, False otherwise
        """
        try:
            start_parts = hora_inicio.split(":")
            end_parts = hora_fin.split(":")

            start_minutes = int(start_parts[0]) * 60 + int(start_parts[1])
            end_minutes = int(end_parts[0]) * 60 + int(end_parts[1])

            return start_minutes < end_minutes
        except (ValueError, IndexError):
            return False
