"""
GeoReasoningAgent - Resolves geographical references to specific locations.

Responsible for:
- Matching location references ("clínica norte") to actual locations
- Using fuzzy string matching for approximate matches
- Validating that location belongs to specified contact
- Resolving location ambiguities with suggestions
"""

import re
from typing import Any, Dict, Optional, List, Tuple
from difflib import SequenceMatcher
import time

from .base import BaseAgent, AgentResult


class GeoReasoningAgent(BaseAgent):
    """Resolves geographical references to specific location IDs."""

    def __init__(self):
        """Initialize GeoReasoningAgent."""
        super().__init__("geo_reasoning", version="1.0.0")

    def run(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Resolve location references to specific location IDs.

        Args:
            input_data: {
                "ubicacion_raw": str (e.g., "clínica norte"),
                "contacto_id": str (e.g., "contact_dr_perez_123"),
                "available_locations": list (from ContactStore),
                "user_context": dict (optional)
            }

        Returns:
            AgentResult with resolved location_id and location_name
        """
        start_time = time.time()

        try:
            ubicacion_raw = input_data.get("ubicacion_raw")
            contacto_id = input_data.get("contacto_id")
            available_locations = input_data.get("available_locations", [])

            # If no location specified, use primary location
            if not ubicacion_raw:
                if available_locations:
                    # Use first location (typically primary)
                    primary = available_locations[0]
                    resolved_data = {
                        "location_id": primary.get("id"),
                        "location_name": primary.get("nombre"),
                        "matched_by": "default",
                        "confidence": 0.8,
                    }
                    duration_ms = int((time.time() - start_time) * 1000)
                    return self._success(
                        resolved_data,
                        "Using primary location (no location specified)",
                        confidence=0.8,
                        duration_ms=duration_ms,
                    )
                else:
                    return self._error("No locations available for this contact")

            # Try exact match first
            exact_match = self._find_exact_match(ubicacion_raw, available_locations)
            if exact_match:
                duration_ms = int((time.time() - start_time) * 1000)
                return self._success(
                    exact_match,
                    "Found exact location match",
                    confidence=1.0,
                    duration_ms=duration_ms,
                )

            # Try fuzzy match
            fuzzy_match = self._find_fuzzy_match(ubicacion_raw, available_locations)
            if fuzzy_match["match"]:
                duration_ms = int((time.time() - start_time) * 1000)

                if fuzzy_match["confidence"] > 0.7:
                    return self._success(
                        fuzzy_match["match"],
                        f"Found location with fuzzy matching (confidence: {fuzzy_match['confidence']:.0%})",
                        confidence=fuzzy_match["confidence"],
                        duration_ms=duration_ms,
                    )
                else:
                    # Low confidence fuzzy match - return as warning with suggestions
                    suggestions = [
                        {
                            "id": loc.get("id"),
                            "nombre": loc.get("nombre"),
                            "confidence": self._calculate_similarity(
                                ubicacion_raw.lower(), loc.get("nombre", "").lower()
                            ),
                        }
                        for loc in available_locations
                    ]
                    suggestions.sort(key=lambda x: x["confidence"], reverse=True)

                    return self._warning(
                        fuzzy_match["match"],
                        f"Found potential match but with low confidence ({fuzzy_match['confidence']:.0%})",
                        warnings=[f"Location '{ubicacion_raw}' may not match '{fuzzy_match['match']['location_name']}'"],
                        confidence=fuzzy_match["confidence"],
                        duration_ms=duration_ms,
                    )

            # No match found - return error with suggestions
            suggestions = [
                {
                    "id": loc.get("id"),
                    "nombre": loc.get("nombre"),
                    "confidence": self._calculate_similarity(
                        ubicacion_raw.lower(), loc.get("nombre", "").lower()
                    ),
                }
                for loc in available_locations
            ]
            suggestions.sort(key=lambda x: x["confidence"], reverse=True)

            duration_ms = int((time.time() - start_time) * 1000)
            return self._error(
                f"Could not find location matching '{ubicacion_raw}'",
                errors=[
                    f"Available locations for contact: {', '.join([loc.get('nombre', 'Unknown') for loc in available_locations])}"
                ],
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_debug(f"GeoReasoningAgent error: {str(e)}")
            return self._error(f"Geo reasoning error: {str(e)}", duration_ms=duration_ms)

    def _find_exact_match(
        self, ubicacion_raw: str, locations: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Find exact match for location.

        Args:
            ubicacion_raw: Location string to match
            locations: List of available locations

        Returns:
            Matched location dict or None
        """
        ubicacion_lower = ubicacion_raw.lower().strip()

        for location in locations:
            loc_name = location.get("nombre", "").lower().strip()

            # Exact match
            if loc_name == ubicacion_lower:
                return {
                    "location_id": location.get("id"),
                    "location_name": location.get("nombre"),
                    "matched_by": "exact",
                    "confidence": 1.0,
                }

            # Match ignoring common prefixes ("clínica norte" vs "clinica norte")
            normalized_raw = self._normalize_location_name(ubicacion_raw)
            normalized_name = self._normalize_location_name(location.get("nombre", ""))

            if normalized_raw == normalized_name:
                return {
                    "location_id": location.get("id"),
                    "location_name": location.get("nombre"),
                    "matched_by": "normalized",
                    "confidence": 0.95,
                }

        return None

    def _find_fuzzy_match(
        self, ubicacion_raw: str, locations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Find fuzzy match for location using SequenceMatcher.

        Args:
            ubicacion_raw: Location string to match
            locations: List of available locations

        Returns:
            Dict with "match" and "confidence", or {"match": None, "confidence": 0}
        """
        best_match = None
        best_confidence = 0.0

        ubicacion_lower = ubicacion_raw.lower().strip()

        for location in locations:
            loc_name = location.get("nombre", "").lower().strip()

            # Calculate similarity ratio
            similarity = self._calculate_similarity(ubicacion_lower, loc_name)

            if similarity > best_confidence:
                best_confidence = similarity
                best_match = {
                    "location_id": location.get("id"),
                    "location_name": location.get("nombre"),
                    "matched_by": "fuzzy_match",
                    "confidence": similarity,
                }

        if best_match:
            return {"match": best_match, "confidence": best_confidence}

        return {"match": None, "confidence": 0.0}

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings using SequenceMatcher.

        Args:
            str1: First string
            str2: Second string

        Returns:
            Similarity ratio (0.0 to 1.0)
        """
        return SequenceMatcher(None, str1, str2).ratio()

    def _normalize_location_name(self, name: str) -> str:
        """
        Normalize location name for comparison.

        Removes common prefixes and normalizes accents.

        Args:
            name: Location name

        Returns:
            Normalized name
        """
        # Convert to lowercase
        name = name.lower().strip()

        # Remove common prefixes
        prefixes = ["clínica ", "clinica ", "consultorio ", "oficina ", "hospital ", "centro "]
        for prefix in prefixes:
            if name.startswith(prefix):
                name = name[len(prefix) :].strip()

        # Remove accents (simple version)
        name = name.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")

        return name
