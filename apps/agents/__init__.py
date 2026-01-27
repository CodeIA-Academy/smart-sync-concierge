"""
AI Agents for Smart-Sync Concierge.

This module implements 6 specialized agents that work together to transform
natural language prompts into structured appointment data.

Architecture:
    1. ParsingAgent - Extracts entities from natural language
    2. TemporalReasoningAgent - Resolves relative dates/times
    3. GeoReasoningAgent - Resolves geographic references
    4. ValidationAgent - Validates extracted data integrity
    5. AvailabilityAgent - Checks real-time availability
    6. NegotiationAgent - Suggests alternatives on conflicts

Pipeline:
    Prompt → Parsing → Temporal → Geo → Validation → Availability → Negotiation → Result
"""

from .base import BaseAgent, AgentResult
from .parsing_agent import ParsingAgent
from .temporal_agent import TemporalReasoningAgent
from .geo_agent import GeoReasoningAgent
from .validation_agent import ValidationAgent
from .availability_agent import AvailabilityAgent
from .negotiation_agent import NegotiationAgent
from .orchestrator import AgentOrchestrator, DecisionTrace

__all__ = [
    "BaseAgent",
    "AgentResult",
    "ParsingAgent",
    "TemporalReasoningAgent",
    "GeoReasoningAgent",
    "ValidationAgent",
    "AvailabilityAgent",
    "NegotiationAgent",
    "AgentOrchestrator",
    "DecisionTrace",
]
