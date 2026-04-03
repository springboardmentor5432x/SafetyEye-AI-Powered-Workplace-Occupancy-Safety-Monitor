"""
Notifier component for the Safety Dashboard.
Sends OS-level desktop notifications when a violation is detected.

Windows: winotify (preferred) → win10toast (fallback)
macOS/Linux: plyer
"""

import sys
from typing import Optional

from detector import ViolationEvent

try:
    from logger import SafetyLogger
except ImportError:
    SafetyLogger = None  # type: ignore[assignment,misc]

_TITLE = "SafetyEye Alert"


class Notifier:
    """Sends cross-platform desktop notifications for violation events."""

    def __init__(self, logger: Optional["SafetyLogger"] = None) -> None:
        self._logger = logger

    def notify(self, event: ViolationEvent) -> None:
        """
        Send a desktop notification for the given ViolationEvent.

        Never raises — any failure is logged as a warning (if a logger is
        provided) and silently swallowed so the dashboard keeps running.
        """
        try:
            body = f"{event.violation_type} detected at {event.timestamp}"

            if sys.platform == "win32":
                self._notify_windows(body)
            else:
                self._notify_plyer(body)

        except Exception as exc:  # noqa: BLE001
            if self._logger is not None:
                try:
                    self._logger.log_violation(
                        # Re-use log_violation for the warning message by
                        # constructing a lightweight proxy event.
                        type("_W", (), {
                            "violation_type": f"[Notifier warning] {exc}",
                            "confidence": 0.0,
                            "timestamp": event.timestamp,
                            "frame_snapshot": None,
                        })()
                    )
                except Exception:  # noqa: BLE001
                    pass  # logger itself failed — nothing more we can do

    # ── Platform helpers ──────────────────────────────────────────────────────

    def _notify_windows(self, body: str) -> None:
        """Try winotify first, fall back to win10toast."""
        try:
            from winotify import Notification  # type: ignore[import]

            toast = Notification(
                app_id="SafetyEye",
                title=_TITLE,
                msg=body,
            )
            toast.show()
        except ImportError:
            # winotify not installed — try win10toast
            from win10toast import ToastNotifier  # type: ignore[import]

            ToastNotifier().show_toast(
                _TITLE,
                body,
                duration=5,
                threaded=True,
            )

    def _notify_plyer(self, body: str) -> None:
        """macOS / Linux notification via plyer."""
        from plyer import notification  # type: ignore[import]

        notification.notify(
            title=_TITLE,
            message=body,
            app_name="SafetyEye",
            timeout=5,
        )
