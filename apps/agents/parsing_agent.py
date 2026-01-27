"""
ParsingAgent - Extracts entities from natural language prompts.

Responsible for:
- Extracting contact names (Dr. Pérez, Dr. García)
- Extracting date references (mañana, próxima semana, 2026-01-24)
- Extracting time references (10am, 14:30, 3pm)
- Extracting location references (clínica norte, consultorio 1)
- Extracting service types (consulta, chequeo, laboratorio)
- Detecting ambiguities and missing information
"""

import re
from typing import Any, Dict, List, Optional
from datetime import datetime
import time

from .base import BaseAgent, AgentResult


class ParsingAgent(BaseAgent):
    """Extracts entities from natural language prompts."""

    def __init__(self):
        """Initialize ParsingAgent."""
        super().__init__("parsing", version="1.0.0")

        # Regex patterns for extraction
        self.patterns = {
            # Contact names (Dr. García, Dra. Pérez, etc.)
            "contact": r"(?:con|with)?\s+(?:dr\.?|dra\.?|doctor|doctora|médico|médica|staff|recurso)\s+([A-ZÁÉÍÓÚa-záéíóú\s\.]+?)(?:\s+(?:en|at|en la|at the)|$)",
            # Time patterns (10am, 14:30, 3pm, etc.)
            "time": r"(\d{1,2}):?(\d{0,2})\s*(?:am|pm|AM|PM|h|:)?|(\d{1,2})\s*(?:am|pm|AM|PM)",
            # Location references (clínica norte, consultorio 1, etc.)
            "location": r"(?:en|at|en la|at the)\s+([A-ZÁÉÍÓÚa-záéíóú\s\d]+?)(?:\s+(?:el|la|los|las)|$)",
            # Service types (consulta, chequeo, laboratorio)
            "service": r"(?:para|for|por|by)\s+(?:una |un |a )?([A-ZÁÉÍÓÚa-záéíóú\s]+?)(?:\s+(?:con|with)|$)",
        }

        # Common date keywords
        self.date_keywords = {
            "hoy": "today",
            "mañana": "tomorrow",
            "pasado mañana": "day_after_tomorrow",
            "próximo": "next",
            "próxima": "next",
            "próximos": "next",
            "próximas": "next",
            "semana": "week",
            "mes": "month",
            "año": "year",
            "lunes": "monday",
            "martes": "tuesday",
            "miércoles": "wednesday",
            "jueves": "thursday",
            "viernes": "friday",
            "sábado": "saturday",
            "domingo": "sunday",
        }

    def run(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Extract entities from prompt.

        Args:
            input_data: {
                "prompt": str,
                "user_timezone": str (optional),
                "user_context": dict (optional)
            }

        Returns:
            AgentResult with extracted entities
        """
        start_time = time.time()

        try:
            prompt = input_data.get("prompt", "").strip()
            if not prompt:
                return self._error("Prompt is empty", duration_ms=0)

            # Convert to lowercase for matching
            prompt_lower = prompt.lower()

            # Extract entities
            contact = self._extract_contact(prompt)
            date_info = self._extract_date(prompt_lower)
            time_info = self._extract_time(prompt_lower)
            location = self._extract_location(prompt)
            service = self._extract_service(prompt)

            # Detect ambiguities
            ambiguities = self._detect_ambiguities(
                contact=contact,
                date_info=date_info,
                time_info=time_info,
                location=location,
                service=service,
            )

            # Calculate confidence
            required_fields_present = sum([
                1 if contact else 0,
                1 if date_info else 0,
            ])
            confidence = required_fields_present / 2.0

            extracted_data = {
                "contacto_nombre": contact,
                "fecha_raw": date_info,
                "hora_raw": time_info,
                "ubicacion": location,
                "servicio": service,
                "ambiguities": ambiguities,
                "raw_prompt": prompt,
            }

            duration_ms = int((time.time() - start_time) * 1000)

            if ambiguities:
                return self._warning(
                    extracted_data,
                    f"Extracted entities but found {len(ambiguities)} ambiguities",
                    warnings=[f"{a['field']}: {a['message']}" for a in ambiguities],
                    confidence=confidence,
                    duration_ms=duration_ms,
                )

            return self._success(
                extracted_data,
                "Successfully extracted entities from prompt",
                confidence=confidence,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_debug(f"ParsingAgent error: {str(e)}")
            return self._error(f"Parsing error: {str(e)}", duration_ms=duration_ms)

    def _extract_contact(self, prompt: str) -> Optional[str]:
        """Extract contact name from prompt."""
        # Simple extraction - matches patterns like "con Dr. Pérez"
        pattern = r"(?:con|with)\s+(?:dr\.?|dra\.?|doctor|doctora|médico|médica)\.?\s+([A-ZÁÉÍÓÚa-záéíóú\s]+?)(?:\s+(?:en|en la|at|at the)|$)"
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Fallback: look for capitalized words after "con"
        pattern = r"con\s+([A-Z][a-záéíóú]+(?:\s+[A-Z][a-záéíóú]+)?)"
        match = re.search(pattern, prompt)
        if match:
            return match.group(1).strip()

        return None

    def _extract_date(self, prompt_lower: str) -> Optional[str]:
        """Extract date reference from prompt."""
        # Check for date keywords
        for keyword, value in self.date_keywords.items():
            if keyword in prompt_lower:
                return keyword

        # Check for explicit dates (YYYY-MM-DD or DD/MM/YYYY)
        date_pattern = r"(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})"
        match = re.search(date_pattern, prompt_lower)
        if match:
            return match.group(1)

        # Check for numbered days (el 24, 25 enero, etc.)
        day_pattern = r"(?:el\s+)?(\d{1,2})\s+(?:de\s+)?(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)?"
        match = re.search(day_pattern, prompt_lower)
        if match:
            return f"day_{match.group(1)}"

        return None

    def _extract_time(self, prompt_lower: str) -> Optional[str]:
        """Extract time reference from prompt."""
        # Pattern for times like "10am", "14:30", "3pm"
        time_pattern = r"(\d{1,2}):?(\d{0,2})\s*(?:am|pm|AM|PM|h)?|(\d{1,2})\s*(?:am|pm|AM|PM)"
        match = re.search(time_pattern, prompt_lower)

        if match:
            if match.group(1):  # Format like "10" or "10:30"
                hour = match.group(1)
                minute = match.group(2) or "00"
                return f"{hour}:{minute}"
            else:  # Format like "3pm"
                hour = match.group(3)
                am_pm = prompt_lower[match.end() - 2 : match.end()]
                return f"{hour}:00 {am_pm}"

        # Check for time keywords (mañana temprano = early morning)
        if "temprano" in prompt_lower or "madrugada" in prompt_lower:
            return "early_morning"
        if "tarde" in prompt_lower:
            return "afternoon"
        if "noche" in prompt_lower:
            return "evening"

        return None

    def _extract_location(self, prompt: str) -> Optional[str]:
        """Extract location reference from prompt."""
        # Pattern for locations after "en" or "at"
        pattern = r"(?:en|at)\s+(?:la\s+)?(?:clínica\s+)?([A-ZÁÉÍÓÚa-záéíóú\s\d]+?)(?:\s+(?:el|la|los|las|\()|$)"
        match = re.search(pattern, prompt, re.IGNORECASE)

        if match:
            location = match.group(1).strip()
            # Remove trailing parentheses or extra text
            location = re.sub(r"\s+\($", "", location)
            return location if location else None

        return None

    def _extract_service(self, prompt: str) -> Optional[str]:
        """Extract service type from prompt."""
        # Pattern for services like "para una consulta", "for checkup"
        pattern = r"(?:para|for)\s+(?:una\s+|un\s+|a\s+)?([A-ZÁÉÍÓÚa-záéíóú\s]+?)(?:\s+(?:con|with|en|at)|$)"
        match = re.search(pattern, prompt, re.IGNORECASE)

        if match:
            service = match.group(1).strip()
            return service if service else None

        # Check for common service keywords
        services = ["consulta", "chequeo", "laboratorio", "radiografía", "ecografía", "revisión"]
        for service in services:
            if service in prompt.lower():
                return service

        return None

    def _detect_ambiguities(
        self,
        contact: Optional[str],
        date_info: Optional[str],
        time_info: Optional[str],
        location: Optional[str],
        service: Optional[str],
    ) -> List[Dict[str, Any]]:
        """
        Detect ambiguous or missing information.

        Returns list of ambiguities with field, message, and possible suggestions.
        """
        ambiguities = []

        if not contact:
            ambiguities.append({
                "field": "contacto",
                "message": "No se especificó qué doctor o contacto",
                "severity": "error",
            })

        if not date_info:
            ambiguities.append({
                "field": "fecha",
                "message": "No se especificó cuándo",
                "severity": "error",
            })

        if not time_info:
            ambiguities.append({
                "field": "hora",
                "message": "No se especificó a qué hora",
                "severity": "warning",
            })

        if not location:
            ambiguities.append({
                "field": "ubicacion",
                "message": "No se especificó en qué ubicación",
                "severity": "info",
            })

        return ambiguities
