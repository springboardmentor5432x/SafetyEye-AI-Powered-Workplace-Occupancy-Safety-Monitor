"""
Alerter component — pure state machine for managing violation alerts.
No Streamlit imports, no threading required.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime,timezone
from typing import List

from detector import ViolationEvent


@dataclass
class AlertState:
    violation_type: str
    detected_at: datetime
    escalated: bool = False
    acknowledged: bool = False


class Alerter:
    """Manages the lifecycle of violation alerts: add, escalate, acknowledge."""

    def __init__(self) -> None:
        self._alerts: List[AlertState] = []

    def add_violation(self, event: ViolationEvent) -> None:
        """Add a new alert for the given violation event.

        If an unacknowledged alert for the same violation_type already exists,
        the duplicate is silently ignored.
        """
        vtype = event.violation_type
        for alert in self._alerts:
            if alert.violation_type == vtype and not alert.acknowledged:
                return
        self._alerts.append(
            AlertState(violation_type=vtype, detected_at=event.timestamp)
        )

    def tick(self, escalation_seconds: int = 5) -> None:
        """Escalate any unacknowledged alert whose age >= escalation_seconds."""
        now = datetime.now(timezone.utc)
        for alert in self._alerts:
            if not alert.acknowledged:
                elapsed = (now - alert.detected_at).total_seconds()
                if elapsed >= escalation_seconds:
                    alert.escalated = True

    def acknowledge(self, violation_type: str) -> None:
        """Mark the matching alert as acknowledged and remove it from the active list."""
        for alert in self._alerts:
            if alert.violation_type == violation_type:
                alert.acknowledged = True
        self._alerts = [a for a in self._alerts if not a.acknowledged]

    def active_alerts(self) -> List[AlertState]:
        """Return all non-acknowledged AlertState objects."""
        return [a for a in self._alerts if not a.acknowledged]
