"""
TemporalReasoningAgent - Resolves relative dates and times to absolute values.

Responsible for:
- Converting "mañana" to absolute date (2026-01-24)
- Converting "10am" to 24-hour format (10:00)
- Converting "próxima semana" to specific dates
- Handling timezone conversions
- Validating times are in business hours
"""

import re
from typing import Any, Dict, Optional, Tuple
from datetime import datetime, timedelta, time
import pytz
import time as time_module

from .base import BaseAgent, AgentResult


class TemporalReasoningAgent(BaseAgent):
    """Resolves temporal references to absolute values."""

    def __init__(self):
        """Initialize TemporalReasoningAgent."""
        super().__init__("temporal_reasoning", version="1.0.0")

        # Business hours (8:00 - 18:00)
        self.business_start = time(8, 0)
        self.business_end = time(18, 0)

    def run(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Resolve temporal references to absolute dates/times.

        Args:
            input_data: {
                "fecha_raw": str (e.g., "mañana", "2026-01-24"),
                "hora_raw": str (e.g., "10am", "14:30"),
                "user_timezone": str (e.g., "America/Mexico_City"),
                "current_datetime": str (ISO 8601, optional)
            }

        Returns:
            AgentResult with resolved fecha and hora_inicio
        """
        start_time = time_module.time()

        try:
            fecha_raw = input_data.get("fecha_raw")
            hora_raw = input_data.get("hora_raw")
            user_timezone = input_data.get("user_timezone", "America/Mexico_City")
            current_datetime_str = input_data.get("current_datetime")

            if not fecha_raw or not hora_raw:
                return self._error("Missing fecha_raw or hora_raw")

            # Get current datetime in user's timezone
            current_dt = self._get_current_datetime(user_timezone, current_datetime_str)

            # Resolve date
            fecha_result = self._resolve_date(fecha_raw, current_dt)
            if not fecha_result:
                return self._error(f"Could not resolve date: {fecha_raw}")

            # Resolve time
            hora_result = self._resolve_time(hora_raw, current_dt)
            if not hora_result:
                return self._error(f"Could not resolve time: {hora_raw}")

            fecha = fecha_result  # YYYY-MM-DD format
            hora_inicio = hora_result["hora"]  # HH:MM format
            hora_fin = hora_result["hora_fin"]  # HH:MM format (default +1 hour)

            # Validate business hours
            hora_time = datetime.strptime(hora_inicio, "%H:%M").time()
            if hora_time < self.business_start or hora_time > self.business_end:
                warnings = [
                    f"Requested time {hora_inicio} is outside business hours ({self.business_start.strftime('%H:%M')} - {self.business_end.strftime('%H:%M')})"
                ]
            else:
                warnings = []

            # Validate date is not in the past
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").replace(tzinfo=current_dt.tzinfo)
            if fecha_dt.date() < current_dt.date():
                return self._error(f"Requested date {fecha} is in the past")

            resolved_data = {
                "fecha": fecha,
                "hora_inicio": hora_inicio,
                "hora_fin": hora_fin,
                "timezone": user_timezone,
                "resolved_datetime": f"{fecha}T{hora_inicio}:00",
            }

            duration_ms = int((time_module.time() - start_time) * 1000)

            if warnings:
                return self._warning(
                    resolved_data,
                    "Resolved datetime but with warnings",
                    warnings=warnings,
                    confidence=0.85,
                    duration_ms=duration_ms,
                )

            return self._success(
                resolved_data,
                "Successfully resolved temporal references",
                confidence=0.95,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = int((time_module.time() - start_time) * 1000)
            self._log_debug(f"TemporalReasoningAgent error: {str(e)}")
            return self._error(f"Temporal resolution error: {str(e)}", duration_ms=duration_ms)

    def _get_current_datetime(
        self, timezone_str: str, current_datetime_str: Optional[str] = None
    ) -> datetime:
        """Get current datetime in specified timezone."""
        try:
            tz = pytz.timezone(timezone_str)
        except pytz.exceptions.UnknownTimeZoneError:
            tz = pytz.timezone("America/Mexico_City")

        if current_datetime_str:
            # Parse ISO 8601 datetime
            try:
                dt = datetime.fromisoformat(current_datetime_str.replace("Z", "+00:00"))
                return dt.astimezone(tz)
            except (ValueError, AttributeError):
                pass

        # Use current time in timezone
        return datetime.now(tz)

    def _resolve_date(self, fecha_raw: str, current_dt: datetime) -> Optional[str]:
        """
        Resolve date reference to YYYY-MM-DD format.

        Args:
            fecha_raw: Raw date string (e.g., "mañana", "2026-01-24")
            current_dt: Current datetime in user's timezone

        Returns:
            Date in YYYY-MM-DD format or None
        """
        fecha_lower = fecha_raw.lower().strip()
        today = current_dt.date()

        # Explicit date format (YYYY-MM-DD)
        if re.match(r"\d{4}-\d{2}-\d{2}", fecha_raw):
            return fecha_raw

        # DD/MM/YYYY or DD-MM-YYYY
        date_match = re.match(r"(\d{2})[-/](\d{2})[-/](\d{4})", fecha_raw)
        if date_match:
            day, month, year = date_match.groups()
            try:
                dt = datetime(int(year), int(month), int(day))
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                return None

        # Relative date keywords
        if "hoy" in fecha_lower:
            return today.strftime("%Y-%m-%d")

        if "mañana" in fecha_lower:
            return (today + timedelta(days=1)).strftime("%Y-%m-%d")

        if "pasado mañana" in fecha_lower or "pasadomañana" in fecha_lower:
            return (today + timedelta(days=2)).strftime("%Y-%m-%d")

        # Week relative (próxima semana)
        if "próxima semana" in fecha_lower or "proxima semana" in fecha_lower:
            # First day of next week (Monday)
            days_ahead = 0 - today.weekday() + 7  # Monday = 0
            return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

        # Specific weekday (próximo lunes, este viernes, etc.)
        weekdays = {
            "lunes": 0,
            "martes": 1,
            "miércoles": 2,
            "miercoles": 2,
            "jueves": 3,
            "viernes": 4,
            "sábado": 5,
            "sabado": 5,
            "domingo": 6,
        }

        for day_name, day_num in weekdays.items():
            if day_name in fecha_lower:
                # Find next occurrence of this weekday
                days_ahead = day_num - today.weekday()
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

        # Day number (el 24, day 25, etc.)
        day_match = re.search(r"(?:el\s+)?(\d{1,2})", fecha_raw)
        if day_match:
            day_num = int(day_match.group(1))
            # Assume same month or next month
            try:
                dt = datetime(today.year, today.month, day_num)
                if dt.date() < today:
                    # Try next month
                    if today.month == 12:
                        dt = datetime(today.year + 1, 1, day_num)
                    else:
                        dt = datetime(today.year, today.month + 1, day_num)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                return None

        return None

    def _resolve_time(self, hora_raw: str, current_dt: datetime) -> Optional[Dict[str, str]]:
        """
        Resolve time reference to HH:MM format.

        Args:
            hora_raw: Raw time string (e.g., "10am", "14:30")
            current_dt: Current datetime in user's timezone

        Returns:
            Dict with "hora" (HH:MM) and "hora_fin" or None
        """
        hora_lower = hora_raw.lower().strip()

        # Explicit time format (HH:MM)
        if re.match(r"\d{1,2}:\d{2}", hora_raw):
            hora = hora_raw
            # Add one hour for end time
            h, m = map(int, hora.split(":"))
            h_fin = (h + 1) % 24
            hora_fin = f"{h_fin:02d}:{m:02d}"
            return {"hora": hora, "hora_fin": hora_fin}

        # Time with am/pm (10am, 3pm, 14:30pm)
        time_match = re.match(r"(\d{1,2}):?(\d{0,2})\s*(am|pm|AM|PM)?", hora_raw)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            am_pm = time_match.group(3)

            # Convert to 24-hour format
            if am_pm:
                am_pm_lower = am_pm.lower()
                if "pm" in am_pm_lower and hour != 12:
                    hour += 12
                elif "am" in am_pm_lower and hour == 12:
                    hour = 0

            hora = f"{hour:02d}:{minute:02d}"

            # Add one hour for end time
            h_fin = (hour + 1) % 24
            m_fin = minute
            hora_fin = f"{h_fin:02d}:{m_fin:02d}"

            return {"hora": hora, "hora_fin": hora_fin}

        # Relative time keywords
        if "temprano" in hora_lower or "madrugada" in hora_lower or "early" in hora_lower:
            return {"hora": "08:00", "hora_fin": "09:00"}

        if "mañana" in hora_lower or "morning" in hora_lower:
            return {"hora": "09:00", "hora_fin": "10:00"}

        if "mediodía" in hora_lower or "noon" in hora_lower:
            return {"hora": "12:00", "hora_fin": "13:00"}

        if "tarde" in hora_lower or "afternoon" in hora_lower:
            return {"hora": "14:00", "hora_fin": "15:00"}

        if "noche" in hora_lower or "evening" in hora_lower:
            return {"hora": "17:00", "hora_fin": "18:00"}

        return None
