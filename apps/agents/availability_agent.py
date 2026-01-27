"""
AvailabilityAgent - Verifies real-time availability against existing data.

Responsible for:
- Checking contact availability for specified date/time
- Detecting appointment conflicts
- Verifying service duration constraints
- Identifying why unavailable (contact closed, conflict, etc.)
"""

from typing import Any, Dict, Optional, List
from datetime import datetime
import time

from .base import BaseAgent, AgentResult


class AvailabilityAgent(BaseAgent):
    """Checks real-time availability."""

    def __init__(self):
        """Initialize AvailabilityAgent."""
        super().__init__("availability", version="1.0.0")

    def run(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Check availability for appointment.

        Args:
            input_data: {
                "contacto_id": str,
                "fecha": str (YYYY-MM-DD),
                "hora_inicio": str (HH:MM),
                "hora_fin": str (HH:MM),
                "ubicacion_id": str (optional),
                "servicio_id": str (optional),
                "stores": dict (AppointmentStore, ContactStore, ServiceStore)
            }

        Returns:
            AgentResult with availability status and conflicts/suggestions
        """
        start_time = time.time()

        try:
            contacto_id = input_data.get("contacto_id")
            fecha = input_data.get("fecha")
            hora_inicio = input_data.get("hora_inicio")
            hora_fin = input_data.get("hora_fin")
            ubicacion_id = input_data.get("ubicacion_id")
            servicio_id = input_data.get("servicio_id")
            stores = input_data.get("stores", {})

            if not all([contacto_id, fecha, hora_inicio, hora_fin]):
                return self._error("Missing required fields for availability check")

            contact_store = stores.get("contact_store")
            apt_store = stores.get("appointment_store")
            service_store = stores.get("service_store")

            if not contact_store or not apt_store:
                return self._error("Missing required stores")

            # Check if contact exists and is active
            contact = contact_store.get_by_id(contacto_id)
            if not contact:
                return self._error(f"Contact not found: {contacto_id}")

            if not contact.get("activo", True):
                return self._error(f"Contact is inactive: {contacto_id}")

            # Check contact availability for date/time/location
            is_available, razon = contact_store.check_availability(
                contacto_id, fecha, hora_inicio, hora_fin, ubicacion_id
            )

            if not is_available:
                duration_ms = int((time.time() - start_time) * 1000)
                return self._error(
                    f"Contact not available: {razon}",
                    errors=[f"Reason: {razon}"],
                    duration_ms=duration_ms,
                )

            # Check for appointment conflicts
            appointment_data = {
                "contacto_id": contacto_id,
                "fecha": fecha,
                "hora_inicio": hora_inicio,
                "hora_fin": hora_fin,
                "ubicacion_id": ubicacion_id or "",
            }

            conflicts = apt_store.check_conflicts(appointment_data)

            if conflicts:
                duration_ms = int((time.time() - start_time) * 1000)
                conflict_descriptions = [
                    f"{c.get('type')}: {c.get('message', 'Conflict detected')}"
                    for c in conflicts
                ]

                return self._error(
                    "Appointment conflicts detected",
                    errors=conflict_descriptions,
                    duration_ms=duration_ms,
                )

            # Check service duration constraints
            if servicio_id and service_store:
                service = service_store.get_by_id(servicio_id)
                if service:
                    duration = self._calculate_duration(hora_inicio, hora_fin)
                    duration_config = service.get("duracion", {})

                    min_duration = duration_config.get("minima", 0)
                    max_duration = duration_config.get("maxima", 120)

                    if duration < min_duration:
                        return self._error(
                            f"Appointment duration {duration}min is less than minimum {min_duration}min",
                            errors=[f"Service requires at least {min_duration} minutes"],
                        )

                    if duration > max_duration:
                        return self._error(
                            f"Appointment duration {duration}min exceeds maximum {max_duration}min",
                            errors=[f"Service allows maximum {max_duration} minutes"],
                        )

            availability_data = {
                "available": True,
                "reason": "Available",
                "conflicts": [],
                "slots_disponibles": [],
            }

            duration_ms = int((time.time() - start_time) * 1000)
            return self._success(
                availability_data,
                "Appointment time is available",
                confidence=0.95,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_debug(f"AvailabilityAgent error: {str(e)}")
            return self._error(f"Availability check error: {str(e)}", duration_ms=duration_ms)

    def _calculate_duration(self, hora_inicio: str, hora_fin: str) -> int:
        """
        Calculate duration in minutes between two times.

        Args:
            hora_inicio: Start time (HH:MM)
            hora_fin: End time (HH:MM)

        Returns:
            Duration in minutes
        """
        try:
            start_parts = hora_inicio.split(":")
            end_parts = hora_fin.split(":")

            start_minutes = int(start_parts[0]) * 60 + int(start_parts[1])
            end_minutes = int(end_parts[0]) * 60 + int(end_parts[1])

            duration = end_minutes - start_minutes
            if duration < 0:
                duration += 24 * 60  # Handle day boundary

            return duration
        except (ValueError, IndexError):
            return 0
