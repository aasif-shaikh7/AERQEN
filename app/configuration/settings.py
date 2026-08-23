"""AERQEN settings (small, safe, local).

Phase 1 has no secrets. Future provider credentials must come from environment
variables (per SECURITY.md / secrets rule), never hard-coded here.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    app_name: str = field(default="aerqen")
    log_level: str = field(default_factory=lambda: os.getenv("AERQEN_LOG_LEVEL", "INFO"))


def load_settings() -> Settings:
    return Settings()