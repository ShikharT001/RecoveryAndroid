"""
RecoverX Logging Configuration
Provides privacy-aware logging with redaction for phone numbers, tokens, and private data.
"""

import logging
import re
from pathlib import Path
from typing import TextIO

# Regex patterns for sensitive data redaction
REDACT_PATTERNS = [
    # Phone numbers e.g. +12345678901, +91-9876543210
    (re.compile(r'(\+?\d{1,3}[-.\s]?)?(\d{10,12})'), r'[REDACTED-PHONE]'),
    # WhatsApp JID: 1234567890@s.whatsapp.net
    (re.compile(r'\b\d{7,15}@(s\.whatsapp\.net|g\.us)\b'), r'[REDACTED-JID]'),
    # Auth tokens / hex keys (32+ chars)
    (re.compile(r'\b[0-9a-fA-F]{32,64}\b'), r'[REDACTED-KEY]'),
]


class RedactingFormatter(logging.Formatter):
    """Logging formatter that redacts sensitive personal & cryptographic tokens."""

    def format(self, record: logging.LogRecord) -> str:
        original = super().format(record)
        redacted = original
        for pattern, replacement in REDACT_PATTERNS:
            redacted = pattern.sub(replacement, redacted)
        return redacted


def setup_logging(log_file: Path | None = None, log_level: int = logging.INFO) -> logging.Logger:
    """Configures the root RecoverX logger with console and optional file handlers."""
    logger = logging.getLogger("recoverx")
    logger.setLevel(log_level)
    logger.handlers.clear()

    formatter = RedactingFormatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s:%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
