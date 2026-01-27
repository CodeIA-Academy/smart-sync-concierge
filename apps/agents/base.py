"""
Base classes for AI agents.

Defines the common interface and data structures for all agents.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, Optional, List
from datetime import datetime
import uuid


@dataclass
class AgentResult:
    """Result from an agent execution."""

    status: str  # "success", "error", "warning"
    data: Dict[str, Any]
    message: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    confidence: float = 1.0
    duration_ms: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return asdict(self)

    def is_success(self) -> bool:
        """Check if agent succeeded."""
        return self.status == "success"

    def is_error(self) -> bool:
        """Check if agent failed."""
        return self.status == "error"


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, agent_name: str, version: str = "1.0.0"):
        """
        Initialize agent.

        Args:
            agent_name: Name of the agent (e.g., "parsing", "temporal")
            version: Agent version for tracking changes
        """
        self.agent_name = agent_name
        self.version = version
        self.logger = self._setup_logger()

    def _setup_logger(self):
        """Setup logging for agent."""
        import logging
        logger = logging.getLogger(f"agents.{self.agent_name}")
        logger.setLevel(logging.DEBUG)
        return logger

    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute agent logic.

        Args:
            input_data: Input data for the agent

        Returns:
            AgentResult with status, data, and metadata
        """
        pass

    def _log_debug(self, message: str, data: Optional[Dict] = None):
        """Log debug message with optional data."""
        if data:
            self.logger.debug(f"{message}: {data}")
        else:
            self.logger.debug(message)

    def _create_result(
        self,
        status: str,
        data: Dict[str, Any],
        message: str,
        confidence: float = 1.0,
        errors: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
        duration_ms: int = 0,
    ) -> AgentResult:
        """
        Create an AgentResult.

        Args:
            status: "success", "error", or "warning"
            data: Result data
            message: Human-readable message
            confidence: Confidence score (0-1)
            errors: List of errors
            warnings: List of warnings
            duration_ms: Execution duration in milliseconds

        Returns:
            AgentResult instance
        """
        return AgentResult(
            status=status,
            data=data,
            message=message,
            confidence=confidence,
            errors=errors or [],
            warnings=warnings or [],
            duration_ms=duration_ms,
        )

    def _success(
        self,
        data: Dict[str, Any],
        message: str = "Success",
        confidence: float = 1.0,
        duration_ms: int = 0,
    ) -> AgentResult:
        """Create successful result."""
        return self._create_result("success", data, message, confidence, duration_ms=duration_ms)

    def _error(
        self,
        message: str,
        errors: Optional[List[str]] = None,
        duration_ms: int = 0,
    ) -> AgentResult:
        """Create error result."""
        return self._create_result("error", {}, message, confidence=0.0, errors=errors, duration_ms=duration_ms)

    def _warning(
        self,
        data: Dict[str, Any],
        message: str,
        warnings: Optional[List[str]] = None,
        confidence: float = 0.5,
        duration_ms: int = 0,
    ) -> AgentResult:
        """Create warning result."""
        return self._create_result(
            "warning",
            data,
            message,
            confidence=confidence,
            warnings=warnings,
            duration_ms=duration_ms,
        )
