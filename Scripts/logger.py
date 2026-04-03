"""
Logger component for the Safety Dashboard.
Writes violation events to hourly rotating log files using loguru.
"""

import sys
from pathlib import Path

from loguru import logger as _loguru

from detector import ViolationEvent


class SafetyLogger:
    """Hourly rotating logger for safety violation events."""

    def __init__(self, log_dir: str) -> None:
        self._log_dir = Path(log_dir)
        self._log_dir.mkdir(parents=True, exist_ok=True)

        log_path = self._log_dir / "safetye_{time:YYYY-MM-DD_HH}.log"

        # Remove default loguru sink, add our rotating file sink
        _loguru.remove()
        _loguru.add(
            str(log_path),
            rotation="1 hour",
            format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
            enqueue=True,  # thread-safe async writes
        )
        self._log_path_pattern = str(log_path)

    def _current_log_file(self) -> Path | None:
        """Return the most recently modified log file in log_dir, or None."""
        files = sorted(self._log_dir.glob("safetye_*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
        return files[0] if files else None

    def log_violation(self, event: ViolationEvent) -> None:
        """Write a violation log entry. Retries once on failure; writes to stderr if retry fails."""
        message = f"VIOLATION | {event.violation_type} | conf={event.confidence:.2f} | {event.timestamp}"

        for attempt in range(2):
            try:
                _loguru.info(message)
                return
            except Exception as exc:  # noqa: BLE001
                if attempt == 0:
                    continue  # retry once
                # Second failure — write to stderr, do not raise
                print(
                    f"[SafetyLogger] Failed to write log entry after retry: {exc}\n"
                    f"  Entry: {message}",
                    file=sys.stderr,
                )

    def get_recent_excerpt(self, n_lines: int = 20) -> str:
        """Return the last n_lines from the current log file, or '' if none exists."""
        log_file = self._current_log_file()
        if log_file is None or not log_file.exists():
            return ""

        try:
            lines = log_file.read_text(encoding="utf-8").splitlines()
            return "\n".join(lines[-n_lines:])
        except OSError:
            return ""
