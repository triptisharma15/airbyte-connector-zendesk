"""Custom record extractors for Zendesk incremental APIs."""

from __future__ import annotations

from typing import Any, List, Mapping

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor


class ZendeskTicketCommentEventsExtractor(RecordExtractor):
    """Extract Comment child_events from incremental ticket_events responses."""

    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        try:
            records = response.json().get("ticket_events") or []
        except requests.exceptions.JSONDecodeError:
            records = []

        events: List[Mapping[str, Any]] = []
        for record in records:
            for event in record.get("child_events", []):
                if event.get("event_type") == "Comment":
                    for prop in ("via_reference_id", "ticket_id", "timestamp"):
                        event[prop] = record.get(prop)
                    if not isinstance(event.get("via"), dict):
                        event["via"] = None
                    events.append(event)
        return events
