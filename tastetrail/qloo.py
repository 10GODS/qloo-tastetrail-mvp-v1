"""Minimal Qloo API v2 client.

The client keeps the credential server-side and exposes only the two calls
needed by the MVP: entity search and recommendation insights.
"""

from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class QlooError(RuntimeError):
    """An upstream Qloo request failed or returned an unusable response."""


class QlooClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None, timeout: float = 15.0):
        # Hackathon-issued credentials are scoped to this host. Production and
        # staging hosts reject them even when the key itself is valid.
        configured_base = os.getenv("QLOO_API_BASE") or os.getenv("QLOO_BASE_URL")
        self.base_url = (base_url or configured_base or "https://hackathon.api.qloo.com").rstrip("/")
        self.api_key = api_key or os.getenv("QLOO_API_KEY")
        self.timeout = timeout

    def _get(self, path: str, params: dict[str, object]) -> dict:
        if not self.api_key:
            raise QlooError("QLOO_API_KEY is not configured")
        query = urlencode({key: value for key, value in params.items() if value not in (None, "")})
        request = Request(
            f"{self.base_url}{path}?{query}",
            headers={"accept": "application/json", "x-api-key": self.api_key},
            method="GET",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise QlooError(f"Qloo returned HTTP {exc.code}: {detail}") from exc
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise QlooError(f"Qloo request failed: {exc}") from exc
        if not isinstance(payload, dict):
            raise QlooError("Qloo returned a non-object JSON response")
        return payload

    def search_entity(self, query: str, entity_type: str = "urn:entity:place", take: int = 12) -> dict:
        return self._get("/search", {"query": query, "types": entity_type, "take": take})

    def insights(
        self,
        interests: list[str],
        location_query: str,
        entity_type: str = "urn:entity:place",
        take: int = 12,
    ) -> dict:
        return self._get(
            "/v2/insights",
            {
                "filter.type": entity_type,
                "signal.interests.entities": ",".join(interests),
                "filter.location.query": location_query,
                "feature.explainability": "true",
                "take": take,
            },
        )

