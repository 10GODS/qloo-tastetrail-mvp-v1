"""Pure planning and response-shaping logic for TasteTrail."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class InsightsClient(Protocol):
    def search_entity(self, query: str, entity_type: str = "urn:entity:place", take: int = 12) -> dict: ...

    def insights(self, interests: list[str], location_query: str, entity_type: str = "urn:entity:place", take: int = 12) -> dict: ...


@dataclass(frozen=True)
class PlanRequest:
    location: str
    interests: tuple[str, ...]
    budget: str = "moderate"
    time_window: str = "one day"
    constraints: tuple[str, ...] = ()


def validate_request(payload: dict[str, Any]) -> PlanRequest:
    location = str(payload.get("location", "")).strip()
    interests = tuple(str(value).strip() for value in payload.get("interests", []) if str(value).strip())
    if not location:
        raise ValueError("location is required")
    if not interests:
        raise ValueError("at least one interest is required")
    if len(interests) > 8:
        raise ValueError("use at most eight interests")
    constraints = tuple(str(value).strip() for value in payload.get("constraints", []) if str(value).strip())
    return PlanRequest(
        location=location,
        interests=interests,
        budget=str(payload.get("budget", "moderate")).strip() or "moderate",
        time_window=str(payload.get("time_window", "one day")).strip() or "one day",
        constraints=constraints,
    )


def _items(payload: dict) -> list[dict]:
    value = payload.get("results", payload.get("entities", []))
    return value if isinstance(value, list) else []


def _entity_id(item: dict) -> str | None:
    for key in ("entity_id", "id", "qid"):
        if item.get(key):
            return str(item[key])
    return None


def _name(item: dict) -> str:
    name = item.get("name") or item.get("entity_name") or item.get("title")
    if name:
        return str(name)
    properties = item.get("properties")
    return str(properties.get("name", "Unnamed place")) if isinstance(properties, dict) else "Unnamed place"


def _affinity(item: dict) -> float | None:
    for key in ("affinity", "score", "value"):
        if isinstance(item.get(key), (int, float)):
            return float(item[key])
    return None


def build_plan(request_payload: dict[str, Any], client: InsightsClient) -> dict[str, Any]:
    request = validate_request(request_payload)
    seeds: list[str] = []
    seed_matches: list[dict[str, str]] = []
    for interest in request.interests:
        response = client.search_entity(interest)
        match = next((item for item in _items(response) if _entity_id(item)), None)
        if match:
            entity_id = _entity_id(match)
            assert entity_id is not None
            seeds.append(entity_id)
            seed_matches.append({"input": interest, "id": entity_id, "name": _name(match)})
    if not seeds:
        raise ValueError("Qloo could not resolve any interest into an entity")
    response = client.insights(seeds, request.location)
    recommendations = []
    for item in _items(response)[:8]:
        recommendations.append(
            {
                "name": _name(item),
                "entity_id": _entity_id(item),
                "affinity": _affinity(item),
                "why": "Qloo affinity match for " + ", ".join(request.interests),
                "source": "Qloo Insights API",
            }
        )
    if not recommendations:
        raise ValueError("Qloo returned no recommendations for this location and taste profile")
    return {
        "location": request.location,
        "budget": request.budget,
        "time_window": request.time_window,
        "constraints": list(request.constraints),
        "resolved_interests": seed_matches,
        "recommendations": recommendations,
        "provenance": "Recommendations are returned from Qloo; hard constraints are user supplied.",
    }

