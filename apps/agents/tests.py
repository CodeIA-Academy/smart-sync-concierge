"""
Tests for AI agents.

Covers unit tests for individual agents and integration tests for the orchestrator.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from .base import AgentResult, BaseAgent
from .parsing_agent import ParsingAgent
from .temporal_agent import TemporalReasoningAgent
from .geo_agent import GeoReasoningAgent
from .validation_agent import ValidationAgent
from .availability_agent import AvailabilityAgent
from .negotiation_agent import NegotiationAgent
from .orchestrator import AgentOrchestrator, DecisionTrace


class TestParsingAgent(unittest.TestCase):
    """Tests for ParsingAgent."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = ParsingAgent()

    def test_extract_contact_name(self):
        """Test contact name extraction."""
        result = self.agent.run({
            "prompt": "cita mañana 10am con Dr. Pérez"
        })
        self.assertTrue(result.is_success() or result.status == "warning")
        self.assertIn("Dr. Pérez", str(result.data))

    def test_extract_date_keyword(self):
        """Test date keyword extraction."""
        result = self.agent.run({
            "prompt": "cita mañana con Dr. García"
        })
        self.assertTrue(result.is_success() or result.status == "warning")
        data = result.data
        self.assertIsNotNone(data.get("fecha_raw"))

    def test_extract_time(self):
        """Test time extraction."""
        result = self.agent.run({
            "prompt": "cita a las 10:30 con Dr. López"
        })
        self.assertTrue(result.is_success() or result.status == "warning")
        data = result.data
        self.assertIsNotNone(data.get("hora_raw"))

    def test_ambiguous_prompt(self):
        """Test detection of ambiguous prompt."""
        result = self.agent.run({
            "prompt": "cita con el doctor"
        })
        # Should warn or error about ambiguities
        self.assertTrue(result.is_error() or result.status == "warning")

    def test_empty_prompt(self):
        """Test handling of empty prompt."""
        result = self.agent.run({
            "prompt": ""
        })
        self.assertTrue(result.is_error())


class TestTemporalReasoningAgent(unittest.TestCase):
    """Tests for TemporalReasoningAgent."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = TemporalReasoningAgent()

    def test_resolve_tomorrow(self):
        """Test resolving 'mañana' to next day."""
        result = self.agent.run({
            "fecha_raw": "mañana",
            "hora_raw": "10:00",
            "user_timezone": "America/Mexico_City"
        })
        self.assertTrue(result.is_success())
        data = result.data
        self.assertIsNotNone(data.get("fecha"))
        self.assertRegex(data.get("fecha"), r"^\d{4}-\d{2}-\d{2}$")

    def test_resolve_time_format(self):
        """Test time format resolution."""
        result = self.agent.run({
            "fecha_raw": "hoy",
            "hora_raw": "10am",
            "user_timezone": "America/Mexico_City"
        })
        self.assertTrue(result.is_success())
        data = result.data
        self.assertEqual(data.get("hora_inicio"), "10:00")

    def test_invalid_time(self):
        """Test handling of invalid time."""
        result = self.agent.run({
            "fecha_raw": None,
            "hora_raw": "invalid",
            "user_timezone": "America/Mexico_City"
        })
        self.assertTrue(result.is_error())

    def test_business_hours_warning(self):
        """Test warning for outside business hours."""
        result = self.agent.run({
            "fecha_raw": "hoy",
            "hora_raw": "23:00",
            "user_timezone": "America/Mexico_City"
        })
        # Should succeed but with warning about business hours
        self.assertTrue(result.status in ["success", "warning"])


class TestGeoReasoningAgent(unittest.TestCase):
    """Tests for GeoReasoningAgent."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = GeoReasoningAgent()
        self.sample_locations = [
            {
                "id": "loc_1",
                "nombre": "Clínica Centro",
                "direccion": "Calle 1"
            },
            {
                "id": "loc_2",
                "nombre": "Clínica Norte",
                "direccion": "Calle 2"
            }
        ]

    def test_exact_location_match(self):
        """Test exact location matching."""
        result = self.agent.run({
            "ubicacion_raw": "Clínica Centro",
            "contacto_id": "contact_1",
            "available_locations": self.sample_locations
        })
        self.assertTrue(result.is_success())
        self.assertEqual(result.data.get("location_name"), "Clínica Centro")

    def test_fuzzy_location_match(self):
        """Test fuzzy location matching."""
        result = self.agent.run({
            "ubicacion_raw": "clinica norte",  # lowercase, no accent
            "contacto_id": "contact_1",
            "available_locations": self.sample_locations
        })
        # Should match despite case/accent differences
        self.assertTrue(result.is_success() or result.status == "warning")

    def test_no_location_specified(self):
        """Test handling when no location is specified."""
        result = self.agent.run({
            "ubicacion_raw": None,
            "contacto_id": "contact_1",
            "available_locations": self.sample_locations
        })
        # Should use default location
        self.assertTrue(result.is_success())


class TestValidationAgent(unittest.TestCase):
    """Tests for ValidationAgent."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = ValidationAgent()

    def test_valid_data(self):
        """Test validation of valid data."""
        result = self.agent.run({
            "contacto_id": "contact_123",
            "fecha": "2026-01-30",
            "hora_inicio": "10:00",
            "hora_fin": "11:00",
            "stores": {}  # No store validation for this test
        })
        self.assertTrue(result.is_success())

    def test_invalid_date_format(self):
        """Test detection of invalid date format."""
        result = self.agent.run({
            "contacto_id": "contact_123",
            "fecha": "30/01/2026",  # Wrong format
            "hora_inicio": "10:00",
            "hora_fin": "11:00",
            "stores": {}
        })
        self.assertTrue(result.is_error())

    def test_invalid_time_range(self):
        """Test detection of invalid time range."""
        result = self.agent.run({
            "contacto_id": "contact_123",
            "fecha": "2026-01-30",
            "hora_inicio": "11:00",
            "hora_fin": "10:00",  # End before start
            "stores": {}
        })
        self.assertTrue(result.is_error())

    def test_missing_required_fields(self):
        """Test detection of missing required fields."""
        result = self.agent.run({
            "contacto_id": "contact_123",
            "fecha": None,  # Missing required field
            "hora_inicio": "10:00",
            "hora_fin": "11:00",
            "stores": {}
        })
        self.assertTrue(result.is_error())


class TestAgentResult(unittest.TestCase):
    """Tests for AgentResult data class."""

    def test_success_result(self):
        """Test creating a success result."""
        result = AgentResult(
            status="success",
            data={"test": "data"},
            message="Success",
            confidence=1.0
        )
        self.assertTrue(result.is_success())
        self.assertFalse(result.is_error())

    def test_error_result(self):
        """Test creating an error result."""
        result = AgentResult(
            status="error",
            data={},
            message="Error",
            errors=["Error 1"],
            confidence=0.0
        )
        self.assertTrue(result.is_error())
        self.assertFalse(result.is_success())

    def test_to_dict(self):
        """Test converting result to dictionary."""
        result = AgentResult(
            status="success",
            data={"test": "data"},
            message="Success",
            confidence=0.95
        )
        result_dict = result.to_dict()
        self.assertEqual(result_dict["status"], "success")
        self.assertEqual(result_dict["message"], "Success")


class TestAgentOrchestrator(unittest.TestCase):
    """Tests for AgentOrchestrator."""

    def setUp(self):
        """Set up test fixtures."""
        self.orchestrator = AgentOrchestrator()

        # Create mock stores
        self.mock_contact_store = MagicMock()
        self.mock_apt_store = MagicMock()
        self.mock_service_store = MagicMock()

        # Configure default mock returns
        self.mock_contact_store.list_all.return_value = [
            {
                "id": "contact_dr_perez",
                "nombre": "Dr. Pérez",
                "activo": True,
                "ubicaciones": [
                    {"id": "loc_1", "nombre": "Clínica Centro"}
                ]
            }
        ]
        self.mock_contact_store.get_by_id.return_value = {
            "id": "contact_dr_perez",
            "nombre": "Dr. Pérez",
            "activo": True,
            "ubicaciones": [
                {"id": "loc_1", "nombre": "Clínica Centro"}
            ]
        }
        self.mock_apt_store.check_conflicts.return_value = []
        self.mock_contact_store.check_availability.return_value = (True, None)

        self.stores = {
            'appointment_store': self.mock_apt_store,
            'contact_store': self.mock_contact_store,
            'service_store': self.mock_service_store,
        }

    def test_orchestrator_initialization(self):
        """Test that orchestrator initializes all agents."""
        self.assertIsNotNone(self.orchestrator.parsing_agent)
        self.assertIsNotNone(self.orchestrator.temporal_agent)
        self.assertIsNotNone(self.orchestrator.geo_agent)
        self.assertIsNotNone(self.orchestrator.validation_agent)
        self.assertIsNotNone(self.orchestrator.availability_agent)
        self.assertIsNotNone(self.orchestrator.negotiation_agent)

    def test_decision_trace_creation(self):
        """Test DecisionTrace creation."""
        trace = DecisionTrace(
            trace_id="trace_test_123",
            timestamp=datetime.now().isoformat(),
            input_prompt="test prompt",
            user_timezone="America/Mexico_City",
            user_id="user123"
        )
        self.assertEqual(trace.trace_id, "trace_test_123")
        self.assertEqual(trace.final_status, "pending")
        self.assertIsInstance(trace.agents, list)


if __name__ == '__main__':
    unittest.main()
