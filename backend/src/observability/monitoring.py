"""Monitoring and incident event emission hooks (T028).

Scaffold sink logs structured monitoring events; production wires this to a
real APM/metrics/incident pipeline behind the same `emit_event` interface.
Confidentiality/integrity/availability/payment/decision incidents must be
recorded and linked to remediation per constitution "Delivery and Quality
Gates".
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.observability.logging import get_logger

INCIDENT_CATEGORIES = frozenset(
    {"confidentiality", "integrity", "availability", "payment", "incorrect_decision"}
)


@dataclass
class MonitoringEvent:
    event_type: str
    correlation_reference: str
    minimized_data: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


_events: list[MonitoringEvent] = []


def emit_event(event: MonitoringEvent) -> None:
    _events.append(event)
    get_logger().info(
        "monitoring_event type=%s correlation=%s", event.event_type, event.correlation_reference
    )


def record_incident(category: str, correlation_reference: str, detail_reference: str) -> None:
    if category not in INCIDENT_CATEGORIES:
        raise ValueError(f"unknown incident category '{category}'")
    emit_event(
        MonitoringEvent(
            event_type=f"incident.{category}",
            correlation_reference=correlation_reference,
            minimized_data={"detail_reference": detail_reference},
        )
    )


def recent_events(limit: int = 100) -> list[MonitoringEvent]:
    return _events[-limit:]
