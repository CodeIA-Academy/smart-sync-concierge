"""
AgentOrchestrator - Orchestrates the pipeline of AI agents.

Responsible for:
- Coordinating execution of 6 agents in sequence
- Handling errors and fallbacks
- Recording DecisionTrace for observability
- Managing overall appointment creation workflow
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional, List
from datetime import datetime
import uuid
import json
import time

from .base import AgentResult
from .parsing_agent import ParsingAgent
from .temporal_agent import TemporalReasoningAgent
from .geo_agent import GeoReasoningAgent
from .validation_agent import ValidationAgent
from .availability_agent import AvailabilityAgent
from .negotiation_agent import NegotiationAgent


@dataclass
class DecisionTrace:
    """Complete trace of all agent decisions."""

    trace_id: str
    timestamp: str
    input_prompt: str
    user_timezone: str
    user_id: str
    agents: List[Dict[str, Any]] = field(default_factory=list)
    final_status: str = "pending"  # pending, success, error, conflict
    final_output: Dict[str, Any] = field(default_factory=dict)
    total_duration_ms: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert trace to dictionary."""
        return asdict(self)


class AgentOrchestrator:
    """Orchestrates AI agent pipeline."""

    def __init__(self):
        """Initialize orchestrator with all agents."""
        self.parsing_agent = ParsingAgent()
        self.temporal_agent = TemporalReasoningAgent()
        self.geo_agent = GeoReasoningAgent()
        self.validation_agent = ValidationAgent()
        self.availability_agent = AvailabilityAgent()
        self.negotiation_agent = NegotiationAgent()

    def process_appointment_prompt(
        self,
        prompt: str,
        user_timezone: str = "America/Mexico_City",
        user_id: str = "anonymous",
        stores: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process appointment prompt through agent pipeline.

        Args:
            prompt: Natural language appointment request
            user_timezone: User's timezone (IANA format)
            user_id: User identifier
            stores: Dict with appointment_store, contact_store, service_store

        Returns:
            Dict with:
            - status: "success", "error", "conflict"
            - data: appointment data or None
            - trace: DecisionTrace object
            - suggestions: alternative slots if conflict
        """
        orchestrator_start = time.time()

        # Create trace
        trace = DecisionTrace(
            trace_id=f"trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now().isoformat(),
            input_prompt=prompt,
            user_timezone=user_timezone,
            user_id=user_id,
        )

        # Initialize result
        result = {
            "status": "error",
            "data": None,
            "message": "Appointment processing failed",
            "trace_id": trace.trace_id,
            "suggestions": [],
        }

        try:
            # ==================== AGENT 1: PARSING ====================
            parsing_result = self.parsing_agent.run({"prompt": prompt, "user_timezone": user_timezone})
            self._record_agent(trace, "parsing", parsing_result)

            if parsing_result.is_error():
                # Check for ambiguities
                if parsing_result.data.get("ambiguities"):
                    result["status"] = "error"
                    result["message"] = "Prompt is ambiguous and requires clarification"
                    result["ambiguities"] = parsing_result.data["ambiguities"]
                else:
                    result["message"] = f"Could not parse prompt: {parsing_result.message}"
                trace.final_status = "error"
                result["trace"] = trace
                return result

            parsed_data = parsing_result.data

            # ==================== AGENT 2: TEMPORAL REASONING ====================
            temporal_input = {
                "fecha_raw": parsed_data.get("fecha_raw"),
                "hora_raw": parsed_data.get("hora_raw"),
                "user_timezone": user_timezone,
            }

            temporal_result = self.temporal_agent.run(temporal_input)
            self._record_agent(trace, "temporal_reasoning", temporal_result)

            if temporal_result.is_error():
                result["message"] = f"Could not resolve date/time: {temporal_result.message}"
                trace.final_status = "error"
                result["trace"] = trace
                return result

            temporal_data = temporal_result.data

            # ==================== AGENT 3: GEOGRAPHICAL REASONING ====================
            # Get contact ID (need to match name to ID)
            contacto_nombre = parsed_data.get("contacto_nombre")
            contacto_id = None

            if stores and contacto_nombre:
                contact_store = stores.get("contact_store")
                if contact_store:
                    # Simple name matching (in production, use better matching)
                    all_contacts = contact_store.list_all()
                    for contact in all_contacts:
                        if contacto_nombre.lower() in contact.get("nombre", "").lower():
                            contacto_id = contact.get("id")
                            break

            if not contacto_id:
                result["message"] = f"Could not find contact: {contacto_nombre}"
                trace.final_status = "error"
                result["trace"] = trace
                return result

            # Get available locations for contact
            available_locations = []
            if stores:
                contact_store = stores.get("contact_store")
                if contact_store:
                    contact = contact_store.get_by_id(contacto_id)
                    if contact:
                        available_locations = contact.get("ubicaciones", [])

            geo_input = {
                "ubicacion_raw": parsed_data.get("ubicacion"),
                "contacto_id": contacto_id,
                "available_locations": available_locations,
            }

            geo_result = self.geo_agent.run(geo_input)
            self._record_agent(trace, "geo_reasoning", geo_result)

            # Geo agent errors are not fatal (location is optional)
            geo_data = geo_result.data if geo_result.is_success() or geo_result.status == "warning" else {}

            # ==================== AGENT 4: VALIDATION ====================
            validation_input = {
                "contacto_id": contacto_id,
                "contacto_nombre": contacto_nombre,
                "fecha": temporal_data.get("fecha"),
                "hora_inicio": temporal_data.get("hora_inicio"),
                "hora_fin": temporal_data.get("hora_fin"),
                "ubicacion_id": geo_data.get("location_id"),
                "servicio_id": parsed_data.get("servicio_id"),
                "stores": stores,
            }

            validation_result = self.validation_agent.run(validation_input)
            self._record_agent(trace, "validation", validation_result)

            if validation_result.is_error():
                result["message"] = f"Validation failed: {validation_result.message}"
                result["errors"] = validation_result.errors
                trace.final_status = "error"
                result["trace"] = trace
                return result

            validated_data = validation_result.data

            # ==================== AGENT 5: AVAILABILITY ====================
            availability_input = {
                "contacto_id": contacto_id,
                "fecha": validated_data.get("fecha"),
                "hora_inicio": validated_data.get("hora_inicio"),
                "hora_fin": validated_data.get("hora_fin"),
                "ubicacion_id": validated_data.get("ubicacion_id"),
                "servicio_id": validated_data.get("servicio_id"),
                "stores": stores,
            }

            availability_result = self.availability_agent.run(availability_input)
            self._record_agent(trace, "availability", availability_result)

            if availability_result.is_error():
                # Availability conflict - need negotiation
                # ==================== AGENT 6: NEGOTIATION ====================
                negotiation_input = {
                    "appointment_data": validated_data,
                    "contacto_id": contacto_id,
                    "fecha": validated_data.get("fecha"),
                    "hora_inicio": validated_data.get("hora_inicio"),
                    "ubicacion_id": validated_data.get("ubicacion_id"),
                    "user_preferences": {"flexible_date": True, "flexible_time": True},
                    "stores": stores,
                }

                negotiation_result = self.negotiation_agent.run(negotiation_input)
                self._record_agent(trace, "negotiation", negotiation_result)

                suggestions = negotiation_result.data.get("suggestions", []) if negotiation_result.is_success() else []

                result["status"] = "conflict"
                result["message"] = "Requested time is not available"
                result["error_detail"] = availability_result.message
                result["suggestions"] = suggestions
                trace.final_status = "conflict"
                result["trace"] = trace
                return result

            # ==================== SUCCESS ====================
            # Prepare final appointment data
            appointment_data = {
                "contacto_id": contacto_id,
                "contacto_nombre": contacto_nombre,
                "fecha": validated_data.get("fecha"),
                "hora_inicio": validated_data.get("hora_inicio"),
                "hora_fin": validated_data.get("hora_fin"),
                "ubicacion_id": validated_data.get("ubicacion_id"),
                "servicio_id": validated_data.get("servicio_id"),
                "status": "confirmed",
                "created_via_agent": True,
                "trace_id": trace.trace_id,
            }

            result["status"] = "success"
            result["message"] = "Appointment successfully created"
            result["data"] = appointment_data
            trace.final_status = "success"
            trace.final_output = appointment_data

            return result

        except Exception as e:
            result["status"] = "error"
            result["message"] = f"Orchestrator error: {str(e)}"
            trace.final_status = "error"
            result["trace"] = trace
            return result

        finally:
            # Record total duration
            trace.total_duration_ms = int((time.time() - orchestrator_start) * 1000)
            result["trace"] = trace

    def _record_agent(self, trace: DecisionTrace, agent_name: str, agent_result: AgentResult):
        """
        Record agent execution in trace.

        Args:
            trace: DecisionTrace object
            agent_name: Name of agent
            agent_result: Result from agent
        """
        trace.agents.append({
            "agent": agent_name,
            "status": agent_result.status,
            "message": agent_result.message,
            "input": {},  # Normally would log input, omitted here
            "output": agent_result.data,
            "duration_ms": agent_result.duration_ms,
            "confidence": agent_result.confidence,
            "errors": agent_result.errors,
            "warnings": agent_result.warnings,
        })
