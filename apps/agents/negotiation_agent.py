"""
NegotiationAgent - Suggests alternative time slots when conflicts occur.

Responsible for:
- Generating alternative time slot suggestions
- Scoring suggestions based on proximity and preferences
- Ranking suggestions by confidence/desirability
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import time

from .base import BaseAgent, AgentResult


class NegotiationAgent(BaseAgent):
    """Generates intelligent suggestions for conflicting appointments."""

    def __init__(self):
        """Initialize NegotiationAgent."""
        super().__init__("negotiation", version="1.0.0")

        # Business hours (8:00 - 18:00)
        self.business_start = 8
        self.business_end = 18
        self.slot_duration = 30  # minutes

    def run(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Generate alternative time slot suggestions.

        Args:
            input_data: {
                "appointment_data": dict (original appointment data),
                "contacto_id": str,
                "fecha": str (YYYY-MM-DD),
                "hora_inicio": str (HH:MM),
                "ubicacion_id": str (optional),
                "user_preferences": dict (optional, flexible_date, flexible_time),
                "stores": dict (AppointmentStore, ContactStore)
            }

        Returns:
            AgentResult with list of suggestions ranked by confidence
        """
        start_time = time.time()

        try:
            contacto_id = input_data.get("contacto_id")
            fecha = input_data.get("fecha")
            hora_inicio = input_data.get("hora_inicio")
            ubicacion_id = input_data.get("ubicacion_id")
            user_preferences = input_data.get("user_preferences", {})
            stores = input_data.get("stores", {})

            if not all([contacto_id, fecha, hora_inicio, stores]):
                return self._error("Missing required fields for negotiation")

            contact_store = stores.get("contact_store")
            apt_store = stores.get("appointment_store")

            if not contact_store or not apt_store:
                return self._error("Missing required stores")

            # Generate suggestions
            suggestions = []

            # Try same-day alternatives (different times)
            same_day_suggestions = self._generate_same_day_suggestions(
                contacto_id, fecha, hora_inicio, ubicacion_id, stores
            )
            suggestions.extend(same_day_suggestions)

            # Try next 3 days at preferred time
            flexible_date = user_preferences.get("flexible_date", True)
            if flexible_date and not same_day_suggestions:
                next_days_suggestions = self._generate_next_days_suggestions(
                    contacto_id, fecha, hora_inicio, ubicacion_id, stores
                )
                suggestions.extend(next_days_suggestions)

            # Rank suggestions by confidence
            suggestions.sort(key=lambda x: x["confidence"], reverse=True)

            # Return top 5 suggestions
            top_suggestions = suggestions[:5]

            suggestion_data = {
                "has_alternatives": len(top_suggestions) > 0,
                "suggestions": top_suggestions,
                "total_suggestions_evaluated": len(suggestions),
            }

            duration_ms = int((time.time() - start_time) * 1000)

            if not top_suggestions:
                return self._warning(
                    suggestion_data,
                    "No alternative slots found",
                    warnings=["Could not find alternative appointment times"],
                    confidence=0.3,
                    duration_ms=duration_ms,
                )

            return self._success(
                suggestion_data,
                f"Generated {len(top_suggestions)} alternative time slot suggestions",
                confidence=0.9,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_debug(f"NegotiationAgent error: {str(e)}")
            return self._error(f"Negotiation error: {str(e)}", duration_ms=duration_ms)

    def _generate_same_day_suggestions(
        self,
        contacto_id: str,
        fecha: str,
        hora_inicio: str,
        ubicacion_id: Optional[str],
        stores: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Generate alternative time slots for the same day.

        Args:
            contacto_id: Contact ID
            fecha: Date (YYYY-MM-DD)
            hora_inicio: Original start time (HH:MM)
            ubicacion_id: Location ID
            stores: Data stores

        Returns:
            List of alternative time slot suggestions
        """
        suggestions = []
        apt_store = stores.get("appointment_store")
        contact_store = stores.get("contact_store")

        if not apt_store or not contact_store:
            return suggestions

        # Generate time slots for this day (30-min intervals)
        slots = []
        for hour in range(self.business_start, self.business_end):
            for minute in [0, 30]:
                time_str = f"{hour:02d}:{minute:02d}"
                slots.append(time_str)

        # Try each slot
        for slot_time in slots:
            # Skip the original time
            if slot_time == hora_inicio:
                continue

            # Calculate end time (assuming 1 hour)
            end_hour = (int(slot_time.split(":")[0]) + 1) % 24
            end_minute = int(slot_time.split(":")[1])
            slot_end = f"{end_hour:02d}:{end_minute:02d}"

            # Check if this slot is available
            appointment_data = {
                "contacto_id": contacto_id,
                "fecha": fecha,
                "hora_inicio": slot_time,
                "hora_fin": slot_end,
                "ubicacion_id": ubicacion_id or "",
            }

            conflicts = apt_store.check_conflicts(appointment_data)
            is_available, razon = contact_store.check_availability(
                contacto_id, fecha, slot_time, slot_end, ubicacion_id
            )

            if not conflicts and is_available:
                # Calculate how close this is to the original time
                original_hour = int(hora_inicio.split(":")[0])
                slot_hour = int(slot_time.split(":")[0])
                hour_diff = abs(slot_hour - original_hour)

                # Higher confidence for closer times
                confidence = max(0.9 - (hour_diff * 0.05), 0.5)

                suggestions.append({
                    "fecha": fecha,
                    "hora_inicio": slot_time,
                    "hora_fin": slot_end,
                    "confidence": confidence,
                    "reason": f"Available slot {hour_diff} hours from requested time",
                })

        return suggestions

    def _generate_next_days_suggestions(
        self,
        contacto_id: str,
        fecha: str,
        hora_inicio: str,
        ubicacion_id: Optional[str],
        stores: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Generate suggestions for next 3 days at preferred time.

        Args:
            contacto_id: Contact ID
            fecha: Original date (YYYY-MM-DD)
            hora_inicio: Preferred time (HH:MM)
            ubicacion_id: Location ID
            stores: Data stores

        Returns:
            List of alternative time slot suggestions
        """
        suggestions = []
        apt_store = stores.get("appointment_store")
        contact_store = stores.get("contact_store")

        if not apt_store or not contact_store:
            return suggestions

        # Try next 3 days
        try:
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            return suggestions

        for days_ahead in [1, 2, 3]:
            future_date = fecha_dt + timedelta(days=days_ahead)
            future_fecha_str = future_date.strftime("%Y-%m-%d")

            # Skip weekends (Saturday = 5, Sunday = 6)
            if future_date.weekday() >= 5:
                continue

            # Calculate end time
            hour_start = int(hora_inicio.split(":")[0])
            minute_start = int(hora_inicio.split(":")[1])
            end_hour = (hour_start + 1) % 24
            hora_fin = f"{end_hour:02d}:{minute_start:02d}"

            # Check availability
            appointment_data = {
                "contacto_id": contacto_id,
                "fecha": future_fecha_str,
                "hora_inicio": hora_inicio,
                "hora_fin": hora_fin,
                "ubicacion_id": ubicacion_id or "",
            }

            conflicts = apt_store.check_conflicts(appointment_data)
            is_available, razon = contact_store.check_availability(
                contacto_id, future_fecha_str, hora_inicio, hora_fin, ubicacion_id
            )

            if not conflicts and is_available:
                confidence = max(0.85 - (days_ahead * 0.1), 0.5)

                suggestions.append({
                    "fecha": future_fecha_str,
                    "hora_inicio": hora_inicio,
                    "hora_fin": hora_fin,
                    "confidence": confidence,
                    "reason": f"Available in {days_ahead} day(s) at same time",
                })

        return suggestions
