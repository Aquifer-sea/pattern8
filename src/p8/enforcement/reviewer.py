"""
Reviewer — Pure Python static rule audit engine (zero API Key).

Check types:
  1. RegexMatch   — Does the output match a required regex pattern?
  2. RegexExclude — Does the output contain a forbidden pattern?
  3. FormatVerify — Does the output match template.yaml structure?
  4. LengthLimit  — Character count, line count limits
  5. Contains     — Does the output contain required text?

If any check fails, raises P8AuditError with detailed violation info.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger("p8.reviewer")


# ════════════════════════════════════════════════════════════
#  P8AuditError — Audit failure exception
# ════════════════════════════════════════════════════════════

class P8AuditError(Exception):
    """
    Custom exception raised when audit fails.

    Carries detailed violation list; MCP layer wraps it as error response.
    """

    def __init__(self, violations: list[dict[str, str]], score: int = 0):
        self.violations = violations
        self.score = score
        summary = "; ".join(v.get("rule", "unknown") + ": " + v.get("message", "") for v in violations[:5])
        super().__init__(f"P8 Audit failed ({len(violations)} violations): {summary}")


# ════════════════════════════════════════════════════════════
#  Reviewer — Static rule engine
# ════════════════════════════════════════════════════════════

class Reviewer:
    """
    Pure Python static audit engine. No LLM calls.
    """

    def __init__(self, guidelines: list[dict[str, Any]], template: str | None = None):
        """
        Args:
            guidelines: rules list from guidelines.yaml
            template:   template string from template.yaml (for FormatVerify)
        """
        self._rules: list[dict[str, Any]] = guidelines or []
        self._template: str = template or ""

    def audit(self, output: str) -> dict[str, Any]:
        """
        Run all rule checks against output.

        Returns:
            {"passed": bool, "score": int, "violations": [...], "checks_total": int, "checks_passed": int}

        Raises:
            P8AuditError: if any rule check fails
        """
        violations: list[dict[str, str]] = []
        checks_total = 0
        checks_passed = 0

        for rule in self._rules:
            rule_type = rule.get("type", "").lower()
            rule_name = rule.get("rule", f"rule_{checks_total + 1}")

            if rule_type == "regex_match":
                checks_total += 1
                ok, msg = self._check_regex(output, rule)
                if ok:
                    checks_passed += 1
                else:
                    violations.append({"rule": rule_name, "type": "regex_match", "message": msg})

            elif rule_type == "regex_exclude":
                checks_total += 1
                ok, msg = self._check_regex_exclude(output, rule)
                if ok:
                    checks_passed += 1
                else:
                    violations.append({"rule": rule_name, "type": "regex_exclude", "message": msg})

            elif rule_type == "format_verify":
                checks_total += 1
                ok, msg = self._check_format(output, rule)
                if ok:
                    checks_passed += 1
                else:
                    violations.append({"rule": rule_name, "type": "format_verify", "message": msg})

            elif rule_type == "length_limit":
                checks_total += 1
                ok, msg = self._check_length(output, rule)
                if ok:
                    checks_passed += 1
                else:
                    violations.append({"rule": rule_name, "type": "length_limit", "message": msg})

            elif rule_type == "contains":
                checks_total += 1
                ok, msg = self._check_contains(output, rule)
                if ok:
                    checks_passed += 1
                else:
                    violations.append({"rule": rule_name, "type": "contains", "message": msg})

            else:
                logger.debug("Skipping unknown rule type: %s", rule_type)

        # Calculate score
        score = int((checks_passed / checks_total * 100)) if checks_total > 0 else 100
        passed = len(violations) == 0

        result = {
            "passed": passed,
            "score": score,
            "checks_total": checks_total,
            "checks_passed": checks_passed,
            "violations": violations,
        }

        logger.info(
            "Audit done | passed=%s | score=%d | %d/%d checks passed | %d violations",
            passed, score, checks_passed, checks_total, len(violations)
        )

        if not passed:
            raise P8AuditError(violations, score)

        return result

    # ────────────────────────────────────────────────────────
    #  RegexMatch — Pattern matching check
    # ────────────────────────────────────────────────────────

    def _check_regex(self, output: str, rule: dict) -> tuple[bool, str]:
        """Check if output matches a required regex pattern."""
        pattern = rule.get("pattern", "")
        if not pattern:
            return True, ""

        flags = re.IGNORECASE if rule.get("case_insensitive", True) else 0
        found = bool(re.search(pattern, output, flags))

        if not found:
            return False, f"Pattern not found: '{pattern}'"
        return True, ""

    def _check_regex_exclude(self, output: str, rule: dict) -> tuple[bool, str]:
        """Check that output does NOT contain a pattern."""
        pattern = rule.get("pattern", "")
        if not pattern:
            return True, ""

        flags = re.IGNORECASE if rule.get("case_insensitive", True) else 0
        found = re.search(pattern, output, flags)

        if found:
            return False, f"Forbidden pattern found: '{pattern}' → '{found.group()[:50]}'"
        return True, ""

    # ────────────────────────────────────────────────────────
    #  FormatVerify — Structure format check
    # ────────────────────────────────────────────────────────

    def _check_format(self, output: str, rule: dict) -> tuple[bool, str]:
        """
        Verify output matches required format structure.

        Supported format types:
        - "json":     Check if output is valid JSON
        - "markdown": Check if output contains required Markdown headings
        - "sections": Check if output contains required section names
        """
        fmt = rule.get("format", "")

        if fmt == "json":
            return self._verify_json(output, rule)
        elif fmt == "markdown":
            return self._verify_markdown_headings(output, rule)
        elif fmt == "sections":
            return self._verify_sections(output, rule)
        else:
            # Use template for check
            if self._template:
                return self._verify_template_sections(output)
            return True, ""

    def _verify_json(self, output: str, rule: dict) -> tuple[bool, str]:
        """Verify valid JSON."""
        # Try to extract JSON from output
        json_start = output.find("{")
        json_end = output.rfind("}") + 1

        if json_start < 0 or json_end <= json_start:
            # Also try JSON array
            json_start = output.find("[")
            json_end = output.rfind("]") + 1

        if json_start < 0 or json_end <= json_start:
            return False, "No JSON structure found"

        try:
            parsed = json.loads(output[json_start:json_end])
            # Check required fields
            required_fields = rule.get("required_fields", [])
            if required_fields and isinstance(parsed, dict):
                missing = [f for f in required_fields if f not in parsed]
                if missing:
                    return False, f"Missing required fields: {missing}"
            return True, ""
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {e}"

    def _verify_markdown_headings(self, output: str, rule: dict) -> tuple[bool, str]:
        """Verify Markdown contains required headings."""
        required_headings = rule.get("headings", [])
        missing = []

        for heading in required_headings:
            pattern = r"^#{1,6}\s+.*" + re.escape(heading)
            if not re.search(pattern, output, re.MULTILINE | re.IGNORECASE):
                missing.append(heading)

        if missing:
            return False, f"Missing headings: {missing}"
        return True, ""

    def _verify_sections(self, output: str, rule: dict) -> tuple[bool, str]:
        """Verify required sections exist."""
        required = rule.get("sections", [])
        missing = [s for s in required if s.lower() not in output.lower()]

        if missing:
            return False, f"Missing sections: {missing}"
        return True, ""

    def _verify_template_sections(self, output: str) -> tuple[bool, str]:
        """Verify format using template headings."""
        headings = re.findall(r"^(#{1,6})\s+(.+)", self._template, re.MULTILINE)
        if not headings:
            return True, ""

        missing = []
        for _, heading_text in headings:
            # Remove [xxx] placeholders
            clean = re.sub(r"\[.*?\]", "", heading_text).strip()
            if clean and clean not in ("...",):
                if clean.lower() not in output.lower():
                    missing.append(clean)

        if missing:
            return False, f"Missing template sections: {missing}"
        return True, ""

    # ────────────────────────────────────────────────────────
    #  LengthLimit — Length constraint check
    # ────────────────────────────────────────────────────────

    def _check_length(self, output: str, rule: dict) -> tuple[bool, str]:
        """Check length constraints."""
        errors = []

        min_chars = rule.get("min_chars")
        if min_chars and len(output) < min_chars:
            errors.append(f"Too few chars: {len(output)} < {min_chars}")

        max_chars = rule.get("max_chars")
        if max_chars and len(output) > max_chars:
            errors.append(f"Too many chars: {len(output)} > {max_chars}")

        lines = output.count("\n") + 1
        min_lines = rule.get("min_lines")
        if min_lines and lines < min_lines:
            errors.append(f"Too few lines: {lines} < {min_lines}")

        max_lines = rule.get("max_lines")
        if max_lines and lines > max_lines:
            errors.append(f"Too many lines: {lines} > {max_lines}")

        if errors:
            return False, "; ".join(errors)
        return True, ""

    # ────────────────────────────────────────────────────────
    #  Contains — Simple content check
    # ────────────────────────────────────────────────────────

    def _check_contains(self, output: str, rule: dict) -> tuple[bool, str]:
        """Check if output contains required text."""
        texts = rule.get("texts", [])
        if isinstance(texts, str):
            texts = [texts]

        missing = []
        for text in texts:
            ci = rule.get("case_insensitive", True)
            if ci:
                if text.lower() not in output.lower():
                    missing.append(text)
            else:
                if text not in output:
                    missing.append(text)

        if missing:
            return False, f"Missing required content: {missing}"
        return True, ""


# ════════════════════════════════════════════════════════════
#  Factory Functions
# ════════════════════════════════════════════════════════════

def load_reviewer(
    guidelines_path: str,
    template_path: str | None = None,
) -> Reviewer:
    """
    Load Reviewer from YAML files.
    """
    rules: list[dict[str, Any]] = []
    try:
        with open(guidelines_path) as f:
            data = yaml.safe_load(f) or {}

        # Support both structured `rules` and legacy `guidelines` formats
        if "rules" in data:
            rules = data["rules"]
        elif "guidelines" in data:
            # Convert legacy string guidelines to contains checks
            for i, g in enumerate(data["guidelines"]):
                if isinstance(g, str):
                    rules.append({
                        "type": "regex_match",
                        "rule": f"guideline_{i + 1}",
                        "pattern": _extract_key_pattern(g),
                        "case_insensitive": True,
                        "description": g,
                    })
                elif isinstance(g, dict):
                    rules.append(g)
    except FileNotFoundError:
        logger.warning("Guidelines not found: %s", guidelines_path)

    # Load template
    template = None
    if template_path:
        try:
            with open(template_path) as f:
                tdata = yaml.safe_load(f) or {}
            template = tdata.get("template", "")
        except FileNotFoundError:
            logger.warning("Template not found: %s", template_path)

    return Reviewer(rules, template)


def _extract_key_pattern(guideline: str) -> str:
    """
    Extract a key check pattern from a legacy guideline string.

    Simple strategy: match any non-empty content (legacy guidelines are advisory).
    """
    return r".+"


async def review_output(
    output: str,
    guidelines_path: str,
    template_path: str | None = None,
    **kwargs,
) -> dict[str, Any]:
    """
    Async audit entry — compatible with MCP calls.

    Returns dict on success, raises P8AuditError on failure.
    """
    reviewer = load_reviewer(guidelines_path, template_path)

    try:
        result = reviewer.audit(output)
        result["action"] = "APPROVED"
        return result
    except P8AuditError:
        raise  # Let MCP layer handle
