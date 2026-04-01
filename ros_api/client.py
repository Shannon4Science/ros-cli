"""HTTP client for ros-api endpoints."""

from __future__ import annotations

import warnings

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ApiError(Exception):
    """Raised when the API returns a non-200 response."""

    def __init__(self, status_code: int, message: str, details=None):
        self.status_code = status_code
        self.message = message
        self.details = details
        super().__init__(f"[{status_code}] {message}")


class RosApiClient:
    """Wraps the 6 ros-api endpoints (metadata & content x query/fetch/batch-fetch)."""

    def __init__(self, api_key: str, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "X-API-Key": api_key,
        })
        self.session.verify = False

    def _post(self, path: str, body: dict) -> dict:
        url = f"{self.base_url}{path}"
        resp = self.session.post(url, json=body, timeout=30)
        data = resp.json()

        meta = data.get("metadata", {})
        code = meta.get("code", resp.status_code)
        if code != 200:
            raise ApiError(
                status_code=code,
                message=meta.get("message", "Unknown error"),
                details=meta.get("details"),
            )
        return data

    # ── Metadata ────────────────────────────────────────────

    def metadata_query(self, **kwargs) -> dict:
        """POST /v1/resources/metadata/query"""
        body = _build_query_body(**kwargs)
        return self._post("/v1/resources/metadata/query", body)

    def metadata_fetch(self, *, identifier: dict, projection: dict | None = None) -> dict:
        """POST /v1/resources/metadata/fetch"""
        body: dict = {"identifier": identifier}
        if projection:
            body["projection"] = projection
        return self._post("/v1/resources/metadata/fetch", body)

    def metadata_batch_fetch(self, *, identifiers: list, projection: dict | None = None) -> dict:
        """POST /v1/resources/metadata/batch-fetch"""
        body: dict = {"identifiers": identifiers}
        if projection:
            body["projection"] = projection
        return self._post("/v1/resources/metadata/batch-fetch", body)

    # ── Content ─────────────────────────────────────────────

    def content_query(self, **kwargs) -> dict:
        """POST /v1/resources/content/query"""
        body = _build_query_body(**kwargs)
        return self._post("/v1/resources/content/query", body)

    def content_fetch(self, *, identifier: dict, projection: dict | None = None) -> dict:
        """POST /v1/resources/content/fetch"""
        body: dict = {"identifier": identifier}
        if projection:
            body["projection"] = projection
        return self._post("/v1/resources/content/fetch", body)

    def content_batch_fetch(self, *, identifiers: list, projection: dict | None = None) -> dict:
        """POST /v1/resources/content/batch-fetch"""
        body: dict = {"identifiers": identifiers}
        if projection:
            body["projection"] = projection
        return self._post("/v1/resources/content/batch-fetch", body)


def _build_query_body(
    *,
    filter: dict | None = None,
    search: dict | None = None,
    projection: dict | None = None,
    pagination: dict | None = None,
    sort: list | None = None,
) -> dict:
    body: dict = {}
    if filter is not None:
        body["filter"] = filter
    if search is not None:
        body["search"] = search
    if projection is not None:
        body["projection"] = projection
    if pagination is not None:
        body["pagination"] = pagination
    if sort is not None:
        body["sort"] = sort
    return body
