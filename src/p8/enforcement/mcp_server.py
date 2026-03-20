"""
P8 MCP Server — Enforcement interface, Agent calls "police" via MCP.

Architecture (aligned with Google ADK Progressive Disclosure):

  Resources (Agent reads on startup, lightweight cognitive base):
    skill://index                    → List available SKILLs
    skill://{name}/skill_md          → SKILL.md pipeline definition
    skill://{name}/checklist         → Entry checklist
    skill://{name}/template          → Output template

  Tools (Agent calls, internal enforcement chain invisible to AI):
    submit_review(content, skill)    → Submit for audit (internal: format + rule check)
    execute_tool(action, skill)      → Request execution (internal: SecurityGuard check)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger("p8.mcp")


# ════════════════════════════════════════════════════════════
#  MCP Tool Router
# ════════════════════════════════════════════════════════════

async def handle_tool_call(tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
    """MCP tool call router (2 tools)."""
    handlers = {
        "submit_review": _handle_submit_review,
        "execute_tool": _handle_execute_tool,
    }

    handler = handlers.get(tool_name)
    if not handler:
        return {"error": f"Unknown tool: {tool_name}"}

    try:
        return await handler(args)
    except Exception as e:
        from p8.enforcement.reviewer import P8AuditError
        if isinstance(e, P8AuditError):
            logger.warning("Audit failed: %d violations", len(e.violations))
            return {
                "error": "P8_AUDIT_FAILED",
                "passed": False,
                "score": e.score,
                "violations": e.violations,
                "action": "REJECTED — Audit failed. Fix the issues in violations and resubmit.",
            }
        logger.exception("Tool call failed: %s", tool_name)
        return {"error": str(e)}


# ════════════════════════════════════════════════════════════
#  submit_review — Submit content for audit (internal chain invisible to AI)
# ════════════════════════════════════════════════════════════

async def _handle_submit_review(args: dict[str, Any]) -> dict[str, Any]:
    """
    Submit content for review. Internal check chain (invisible to Agent):
      1. Load guidelines.yaml (invisible to AI)
      2. Load template.yaml (for format comparison)
      3. Reviewer.audit(content) — 5 static checks
      4. All pass → APPROVED / Violations → P8AuditError
    """
    from p8.enforcement.reviewer import review_output

    content = args.get("content", "")
    skill_name = args.get("skill", "example")

    # Internally load rules (Agent doesn't know these files exist)
    guidelines_path = _find_skill_file(skill_name, "references/guidelines.yaml")
    template_path = _find_skill_file(skill_name, "assets/template.yaml")

    # Audit — raises P8AuditError on failure, caught by handle_tool_call
    return await review_output(content, guidelines_path, template_path)


# ════════════════════════════════════════════════════════════
#  execute_tool — Request OS action (security sandbox)
# ════════════════════════════════════════════════════════════

async def _handle_execute_tool(args: dict[str, Any]) -> dict[str, Any]:
    """Request OS action execution. Internally checked by SecurityGuard."""
    from p8.enforcement.security_guard import load_security_config

    skill_name = args.get("skill", "example")

    # Internally load security rules (Agent doesn't know the check rules)
    security_yaml = _find_skill_file(skill_name, "references/security.yaml")
    guard = load_security_config(security_yaml)

    results = {}

    # Check command
    command = args.get("command")
    if command:
        results["command_check"] = guard.check_command(command)

    # Check path
    path = args.get("path")
    if path:
        operation = args.get("operation", "read")
        results["path_check"] = guard.check_path(path, operation)

    # Summary
    all_allowed = all(v.get("allowed", True) for v in results.values())
    results["allowed"] = all_allowed

    if not all_allowed:
        results["action"] = "BLOCKED — You MUST abort this operation"

    return results


# ════════════════════════════════════════════════════════════
#  Resource Reading
# ════════════════════════════════════════════════════════════

async def handle_read_resource(uri: str) -> str:
    """
    Read MCP Resource content.

    URI format:
      skill://index                → List all SKILLs
      skill://{name}/skill_md      → SKILL.md content
      skill://{name}/checklist     → checklist.yaml content
      skill://{name}/template      → template.yaml content
    """
    if uri == "skill://index":
        return _read_skill_index()

    # Parse skill://{name}/{resource_type}
    parts = uri.replace("skill://", "").split("/")
    if len(parts) != 2:
        return json.dumps({"error": f"Invalid URI: {uri}"})

    skill_name, resource_type = parts

    if resource_type == "skill_md":
        return _read_file_content(skill_name, "SKILL.md")
    elif resource_type == "checklist":
        return _read_yaml_field(skill_name, "assets/checklist.yaml", "checklist")
    elif resource_type == "template":
        return _read_yaml_field(skill_name, "assets/template.yaml", "template")
    else:
        return json.dumps({"error": f"Unknown resource: {resource_type}"})


def _read_skill_index() -> str:
    """List all available skills."""
    skills_dir = Path("skills")
    if not skills_dir.exists():
        return json.dumps({"skills": [], "error": "skills/ directory not found"})

    skills = []
    for d in sorted(skills_dir.iterdir()):
        if d.is_dir() and (d / "SKILL.md").exists():
            try:
                import frontmatter
                post = frontmatter.load(str(d / "SKILL.md"))
                desc = post.metadata.get("description", "")
            except Exception:
                desc = ""
            skills.append({"name": d.name, "description": desc})

    return json.dumps({"skills": skills, "total": len(skills)}, ensure_ascii=False)


def _read_file_content(skill_name: str, rel_path: str) -> str:
    """Read raw SKILL file content."""
    path = _find_skill_file(skill_name, rel_path)
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return json.dumps({"error": f"Not found: {path}"})


def _read_yaml_field(skill_name: str, rel_path: str, field: str) -> str:
    """Read specific field from YAML file."""
    path = _find_skill_file(skill_name, rel_path)
    try:
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        return json.dumps({
            "skill": skill_name,
            field: data.get(field, []),
        }, ensure_ascii=False, indent=2)
    except FileNotFoundError:
        return json.dumps({"error": f"Not found: {path}"})


# ════════════════════════════════════════════════════════════
#  Helpers
# ════════════════════════════════════════════════════════════

def _find_skill_file(skill_name: str, rel_path: str) -> str:
    """Find SKILL file path."""
    candidates = [
        Path("skills") / skill_name / rel_path,
        Path(f".p8/skills/{skill_name}/{rel_path}"),
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return str(candidates[0])


# ════════════════════════════════════════════════════════════
#  MCP Server main entry
# ════════════════════════════════════════════════════════════

async def main():
    """
    Start MCP server (stdio mode).

    Exposes 3 Resources + 2 Tools:
      Resources: skill://index, skill://{name}/checklist, skill://{name}/template
      Tools: submit_review, execute_tool
    """
    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server

        server = Server("pattern8")

        # ── Resources (cognitive base Agent reads on startup) ──

        @server.list_resources()
        async def list_resources():
            from mcp.types import Resource as McpResource

            resources = [
                McpResource(
                    uri="skill://index",
                    name="Available Skills",
                    description="List all available SKILL constraints in the project",
                    mimeType="application/json",
                ),
            ]

            # Dynamically add Resources for each SKILL
            skills_dir = Path("skills")
            if skills_dir.exists():
                for d in sorted(skills_dir.iterdir()):
                    if d.is_dir() and (d / "SKILL.md").exists():
                        name = d.name
                        resources.extend([
                            McpResource(
                                uri=f"skill://{name}/skill_md",
                                name=f"{name} — Pipeline Definition",
                                description=f"SKILL.md for {name}",
                                mimeType="text/markdown",
                            ),
                            McpResource(
                                uri=f"skill://{name}/checklist",
                                name=f"{name} — Entry Checklist",
                                description=f"Inversion checklist for {name}",
                                mimeType="application/json",
                            ),
                            McpResource(
                                uri=f"skill://{name}/template",
                                name=f"{name} — Output Template",
                                description=f"Generator template for {name}",
                                mimeType="application/json",
                            ),
                        ])

            return resources

        @server.read_resource()
        async def read_resource(uri):
            content = await handle_read_resource(str(uri))
            return content

        # ── Tools (enforcement interface Agent calls) ──

        @server.list_tools()
        async def list_tools():
            from mcp.types import Tool
            return [
                Tool(
                    name="submit_review",
                    description=(
                        "Submit content for review. Engine runs format + rule audit internally. "
                        "Returns APPROVED on pass, or violation details on failure."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "Content to review"},
                            "skill": {"type": "string", "description": "SKILL name"},
                        },
                        "required": ["content"]
                    }
                ),
                Tool(
                    name="execute_tool",
                    description=(
                        "Request OS action (command or file operation). "
                        "Engine checks safety internally. Allows if safe, blocks if dangerous."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "Command to execute"},
                            "path": {"type": "string", "description": "Path to operate on"},
                            "operation": {
                                "type": "string",
                                "enum": ["read", "write", "delete"],
                                "description": "Operation type",
                            },
                            "skill": {"type": "string", "description": "SKILL name"},
                        }
                    }
                ),
            ]

        @server.call_tool()
        async def call_tool(name: str, arguments: dict):
            from mcp.types import TextContent
            result = await handle_tool_call(name, arguments)
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    except ImportError:
        logger.error("MCP dependency not installed. Run: pip install 'pattern8[enforcement]'")
        raise
