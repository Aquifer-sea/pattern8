"""
SecurityGuard — Security fence enforcer (Tool Wrapper's police).

This module blocks dangerous operations at code level — Agent CANNOT bypass:
- Blacklist command interception (regex matching)
- Path restriction enforcement
- Write protection toggle
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger("p8.security")


class SecurityGuard:
    """
    Security Guard — three defense fences.

    This is code-level "police", not prompt-level "suggestion".
    """

    def __init__(
        self,
        blacklist: list[str] | None = None,
        allowed_paths: list[str] | None = None,
        denied_paths: list[str] | None = None,
        write_protection: bool = True,
    ):
        # Compile blacklist regex patterns
        self._blacklist_patterns: list[re.Pattern] = []
        for pattern in (blacklist or []):
            regex = pattern.replace("*", ".*")
            self._blacklist_patterns.append(re.compile(regex, re.IGNORECASE))

        self._allowed_paths = [Path(p).resolve() for p in (allowed_paths or [])]
        self._denied_paths = [Path(p).expanduser().resolve() for p in (denied_paths or [])]
        self._write_protection = write_protection

    def check_command(self, command: str) -> dict[str, Any]:
        """
        Check if a command is safe. Returns {"allowed": True/False, "reason": "..."}.
        """
        for pattern in self._blacklist_patterns:
            if pattern.search(command):
                reason = f"Command matches blacklist: {pattern.pattern}"
                logger.warning("🚫 Security blocked: %s → %s", command[:50], reason)
                return {"allowed": False, "reason": reason, "fence": "blacklist"}

        return {"allowed": True, "reason": "Passed"}

    def check_path(self, path: str, operation: str = "read") -> dict[str, Any]:
        """
        Check if path access is safe.
        """
        resolved = Path(path).resolve()

        # Write protection check
        if operation in ("write", "delete", "create") and self._write_protection:
            reason = "Write protection enabled"
            logger.warning("🚫 Write blocked: %s", path)
            return {"allowed": False, "reason": reason, "fence": "write_protection"}

        # Denied path check
        for denied in self._denied_paths:
            if resolved == denied or str(resolved).startswith(str(denied)):
                reason = f"Path in denied list: {denied}"
                logger.warning("🚫 Path blocked: %s", path)
                return {"allowed": False, "reason": reason, "fence": "path_denied"}

        # Allowed path check
        if self._allowed_paths:
            for allowed in self._allowed_paths:
                if resolved == allowed or str(resolved).startswith(str(allowed)):
                    return {"allowed": True, "reason": "Passed"}
            reason = "Path not in allowed list"
            return {"allowed": False, "reason": reason, "fence": "path_not_allowed"}

        return {"allowed": True, "reason": "Passed"}


def load_security_config(security_yaml_path: str) -> SecurityGuard:
    """
    Load security config from security.yaml and create SecurityGuard.
    """
    try:
        with open(security_yaml_path) as f:
            data = yaml.safe_load(f) or {}
    except FileNotFoundError:
        logger.warning("Security config not found, using defaults")
        return SecurityGuard()

    tool_sec = data.get("tool_security", {})
    return SecurityGuard(
        blacklist=tool_sec.get("blacklist", []),
        allowed_paths=tool_sec.get("allowed_paths", []),
        denied_paths=tool_sec.get("denied_paths", []),
        write_protection=tool_sec.get("write_protection", True),
    )
