"""
Configuration loader for the Safety Dashboard.
Reads and validates all required environment variables from a .env file.
"""

import sys
from dataclasses import dataclass

from dotenv import load_dotenv
import os


REQUIRED_VARS = [
    "WEBCAM_INDEX",
    "MODEL_PATH",
    "CONFIDENCE_THRESHOLD",
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USER",
    "SMTP_PASSWORD",
    "SUPERVISOR_EMAIL",
    "LOG_DIR",
]


@dataclass
class AppConfig:
    webcam_index: int          # WEBCAM_INDEX
    model_path: str            # MODEL_PATH
    confidence: float          # CONFIDENCE_THRESHOLD
    smtp_host: str             # SMTP_HOST
    smtp_port: int             # SMTP_PORT
    smtp_user: str             # SMTP_USER
    smtp_password: str         # SMTP_PASSWORD
    supervisor_email: str      # SUPERVISOR_EMAIL
    log_dir: str               # LOG_DIR


def load_config() -> AppConfig:
    """
    Load and validate all required environment variables from a .env file.
    Exits with sys.exit(1) and a descriptive error message if any variable is missing.
    """
    load_dotenv()

    for var in REQUIRED_VARS:
        if not os.environ.get(var):
            print(
                f"[config] ERROR: Required environment variable '{var}' is missing. "
                f"Please set it in your .env file.",
                file=sys.stderr,
            )
            sys.exit(1)

    try:
        webcam_index = int(os.environ["WEBCAM_INDEX"])
    except ValueError:
        print(
            "[config] ERROR: WEBCAM_INDEX must be an integer.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        confidence = float(os.environ["CONFIDENCE_THRESHOLD"])
    except ValueError:
        print(
            "[config] ERROR: CONFIDENCE_THRESHOLD must be a float.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        smtp_port = int(os.environ["SMTP_PORT"])
    except ValueError:
        print(
            "[config] ERROR: SMTP_PORT must be an integer.",
            file=sys.stderr,
        )
        sys.exit(1)

    return AppConfig(
        webcam_index=webcam_index,
        model_path=os.environ["MODEL_PATH"],
        confidence=confidence,
        smtp_host=os.environ["SMTP_HOST"],
        smtp_port=smtp_port,
        smtp_user=os.environ["SMTP_USER"],
        smtp_password=os.environ["SMTP_PASSWORD"],
        supervisor_email=os.environ["SUPERVISOR_EMAIL"],
        log_dir=os.environ["LOG_DIR"],
    )
