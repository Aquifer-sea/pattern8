"""
P8 CLI — SKILL management tools.

Provides list / validate / new / init / serve / mcp-config subcommands
for managing SKILL constraint files in your project.

P8 does NOT call LLMs — it's a rules framework that Agents read and follow.
"""

from __future__ import annotations

import json
from pathlib import Path

import click


# ════════════════════════════════════════════════════════════
#  Main command group
# ════════════════════════════════════════════════════════════

@click.group()
@click.version_option(package_name="pattern8")
def main():
    """
    🎱 Pattern 8 (P8) — AI Agent Governance Framework.
    Constrain how Agents work on your project.
    """
    pass


# ════════════════════════════════════════════════════════════
#  p8 list — List available skills
# ════════════════════════════════════════════════════════════

@main.command("list")
@click.option("--dir", "-d", "skills_dir", default="skills", help="Skills directory")
def list_skills(skills_dir: str):
    """
    List all available SKILLs.
    """
    skills_path = Path(skills_dir)
    if not skills_path.exists():
        click.echo(click.style(f"❌ Directory not found: {skills_path}", fg="red"))
        raise SystemExit(1)

    click.echo(click.style("\n🎱 Available Skills\n", fg="cyan", bold=True))

    found = 0
    for d in sorted(skills_path.iterdir()):
        if d.is_dir() and (d / "SKILL.md").exists():
            found += 1
            try:
                import frontmatter
                post = frontmatter.load(str(d / "SKILL.md"))
                desc = post.metadata.get("description", "")
            except Exception:
                desc = ""

            click.echo(f"  📋 {d.name}")
            if desc:
                click.echo(f"     {desc}")

            # Check asset completeness
            assets = []
            if (d / "assets" / "checklist.yaml").exists():
                assets.append("checklist")
            if (d / "assets" / "template.yaml").exists():
                assets.append("template")
            if (d / "references" / "guidelines.yaml").exists():
                assets.append("guidelines")
            if (d / "references" / "security.yaml").exists():
                assets.append("security")
            click.echo(f"     Assets: {', '.join(assets)}")
            click.echo()

    if found == 0:
        click.echo("  (No skills found)")
    else:
        click.echo(f"  Total: {found} skill(s)\n")


# ════════════════════════════════════════════════════════════
#  p8 validate — Validate SKILL integrity
# ════════════════════════════════════════════════════════════

@main.command()
@click.argument("skill_path")
def validate(skill_path: str):
    """
    Validate SKILL configuration integrity.
    """
    skill_dir = Path(skill_path)
    if skill_dir.is_file():
        skill_dir = skill_dir.parent

    click.echo(click.style(f"\n🔍 Validating: {skill_dir.name}\n", fg="cyan", bold=True))

    errors = []
    warnings = []

    # Check SKILL.md
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md missing")
    else:
        try:
            import frontmatter
            post = frontmatter.load(str(skill_md))
            meta = post.metadata
            if not meta.get("name"):
                warnings.append("SKILL.md missing 'name' field")
            if not meta.get("assets"):
                warnings.append("SKILL.md missing 'assets' config")
            click.echo(f"  ✅ SKILL.md — name: {meta.get('name', '?')}")
        except Exception as e:
            errors.append(f"SKILL.md parse error: {e}")

    # Check required files
    required_files = {
        "assets/checklist.yaml": "Checklist",
        "assets/template.yaml": "Template",
        "references/guidelines.yaml": "Guidelines",
        "references/security.yaml": "Security rules",
    }

    for rel_path, label in required_files.items():
        full_path = skill_dir / rel_path
        if full_path.exists():
            try:
                import yaml
                with open(full_path) as f:
                    yaml.safe_load(f)
                click.echo(f"  ✅ {rel_path} — {label}")
            except Exception as e:
                errors.append(f"{rel_path} YAML error: {e}")
        else:
            warnings.append(f"{rel_path} missing ({label})")

    # Summary
    click.echo()
    if errors:
        for e in errors:
            click.echo(click.style(f"  ❌ {e}", fg="red"))
    if warnings:
        for w in warnings:
            click.echo(click.style(f"  ⚠️  {w}", fg="yellow"))
    if not errors and not warnings:
        click.echo(click.style("  ✅ All checks passed!", fg="green", bold=True))
    elif not errors:
        click.echo(click.style(f"\n  ⚠️  {len(warnings)} warning(s), 0 error(s)", fg="yellow"))
    else:
        click.echo(click.style(f"\n  ❌ {len(errors)} error(s), {len(warnings)} warning(s)", fg="red"))
        raise SystemExit(1)
    click.echo()


# ════════════════════════════════════════════════════════════
#  p8 new — Create a new SKILL
# ════════════════════════════════════════════════════════════

@main.command("new")
@click.argument("skill_name")
@click.option("--dir", "-d", "skills_dir", default="skills", help="Parent directory")
def new_skill(skill_name: str, skills_dir: str):
    """
    Create a new SKILL scaffold.
    """
    skill_dir = Path(skills_dir) / skill_name
    if skill_dir.exists():
        click.echo(click.style(f"❌ SKILL already exists: {skill_dir}", fg="red"))
        raise SystemExit(1)

    click.echo(click.style(f"\n🎱 Creating SKILL: {skill_name}\n", fg="cyan", bold=True))

    (skill_dir / "assets").mkdir(parents=True)
    (skill_dir / "references").mkdir(parents=True)

    title = skill_name.replace("_", " ").replace("-", " ").title()

    (skill_dir / "SKILL.md").write_text(f"""---
name: {skill_name}
description: Describe what this SKILL constrains the Agent to do
assets:
  checklist: assets/checklist.yaml
  template: assets/template.yaml
references:
  guidelines: references/guidelines.yaml
  security: references/security.yaml
---

# {title}

[Describe how this SKILL constrains Agent behavior]

<PIPELINE>

## Step 1: Inversion (Requirements Alignment)
Agent must check every item in `assets/checklist.yaml` before starting.
If any required information is missing, Agent must **block and ask**, never skip.

## Step 2: Generator (Constrained Output)
Agent must strictly follow the format defined in `assets/template.yaml`.
No freestyle — every template field must be filled.

## Step 3: Tool Wrapper (Security Fence)
If tool calls are needed, Agent must check `references/security.yaml` first.
Blacklisted operations must be blocked immediately.

## Step 4: Reviewer (Self-Audit Loop)
Agent must audit its output against `references/guidelines.yaml`.
If non-compliant, roll back to Step 2 and regenerate, up to 3 retries.

</PIPELINE>
""")

    (skill_dir / "assets" / "checklist.yaml").write_text(f"""# {skill_name} Checklist
# Agent must confirm ALL items before starting work
checklist:
  - "Add checklist items here"
""")

    (skill_dir / "assets" / "template.yaml").write_text(f"""# {skill_name} Output Template
# Agent must output in exactly this format
template: |
  # Output Title

  ## Section 1
  [Content]

  ## Section 2
  [Content]
""")

    (skill_dir / "references" / "guidelines.yaml").write_text(f"""# {skill_name} Audit Guidelines
# Agent audits its own output against these standards
guidelines:
  - "Add audit guidelines here"
""")

    (skill_dir / "references" / "security.yaml").write_text(f"""# {skill_name} Security Red Lines
# Agent must NEVER violate these rules
security:
  - "Add security rules here"
""")

    click.echo("  ✅ SKILL.md")
    click.echo("  ✅ assets/checklist.yaml")
    click.echo("  ✅ assets/template.yaml")
    click.echo("  ✅ references/guidelines.yaml")
    click.echo("  ✅ references/security.yaml")
    click.echo(click.style(f"\n  🎉 SKILL created: {skill_dir}\n", fg="green", bold=True))
    click.echo("  Edit these files to define your Agent constraints.\n")


# ════════════════════════════════════════════════════════════
#  p8 init — Initialize P8 in a project
# ════════════════════════════════════════════════════════════

@main.command("init")
@click.argument("target", default=".")
def init_project(target: str):
    """
    Initialize P8 governance in a project.

    Usage:
        p8 init            # In current directory
        p8 init my-project # Create new directory
    """
    import shutil

    target_path = Path(target).resolve()

    click.echo(click.style("\n🎱 Initializing P8\n", fg="cyan", bold=True))

    # Create target directory
    if not target_path.exists():
        target_path.mkdir(parents=True)
        click.echo(f"  📁 Created: {target_path}")

    # Find P8 bundled resources
    p8_root = Path(__file__).parent
    # Dev mode: skills/ at project root
    # Installed mode: skills/ packaged in p8/scaffold/skills/
    dev_skills = p8_root.parent.parent / "skills"
    pkg_skills = p8_root / "scaffold" / "skills"
    dev_agents = p8_root.parent.parent / "AGENTS.md"
    pkg_agents = p8_root / "scaffold" / "AGENTS.md"

    source_skills = dev_skills if dev_skills.exists() else pkg_skills
    source_agents = dev_agents if dev_agents.exists() else pkg_agents

    # 1. Copy AGENTS.md
    agents_dest = target_path / "AGENTS.md"
    if agents_dest.exists():
        click.echo("  ⏭️  AGENTS.md already exists, skipping")
    elif source_agents.exists():
        shutil.copy2(str(source_agents), str(agents_dest))
        click.echo("  ✅ AGENTS.md")
    else:
        # Generate minimal version
        agents_dest.write_text(_MINIMAL_AGENTS_MD)
        click.echo("  ✅ AGENTS.md (minimal)")

    # 2. Copy all built-in SKILLs
    skills_dest = target_path / "skills"
    if skills_dest.exists():
        click.echo("  ⏭️  skills/ already exists, skipping")
    elif source_skills.exists():
        skills_dest.mkdir()
        copied = 0
        for skill_dir in sorted(source_skills.iterdir()):
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                shutil.copytree(str(skill_dir), str(skills_dest / skill_dir.name))
                copied += 1
        if copied > 0:
            click.echo(f"  ✅ skills/ ({copied} built-in SKILLs)")
        else:
            click.echo("  ⚠️  No built-in SKILLs found")
    else:
        click.echo("  ⚠️  Built-in resources not found")

    # 3. Generate .gitignore
    gitignore = target_path / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("__pycache__/\n*.pyc\n.venv/\n.env\n")
        click.echo("  ✅ .gitignore")

    # 4. Install Git pre-commit hook
    git_hooks_dir = target_path / ".git" / "hooks"
    if git_hooks_dir.exists():
        dev_hook = p8_root.parent.parent / "hooks" / "pre-commit"
        pkg_hook = p8_root / "scaffold" / "hooks" / "pre-commit"
        source_hook = dev_hook if dev_hook.exists() else pkg_hook
        hook_dest = git_hooks_dir / "pre-commit"
        if hook_dest.exists():
            click.echo("  ⏭️  pre-commit hook already exists, skipping")
        elif source_hook.exists():
            shutil.copy2(str(source_hook), str(hook_dest))
            hook_dest.chmod(0o755)
            click.echo("  ✅ .git/hooks/pre-commit (auto-audit on commit)")
        else:
            click.echo("  ⚠️  Hook template not found")
    else:
        click.echo("  ⏭️  Not a git repo, skipping hook")

    # 5. Install Cursor Rules
    cursor_rules_dir = target_path / ".cursor" / "rules"
    dev_rules = p8_root.parent.parent / ".cursor" / "rules" / "p8-enforcement.mdc"
    pkg_rules = p8_root / "scaffold" / "cursor-rules" / "p8-enforcement.mdc"
    source_rules = dev_rules if dev_rules.exists() else pkg_rules
    rules_dest = cursor_rules_dir / "p8-enforcement.mdc"
    if rules_dest.exists():
        click.echo("  ⏭️  Cursor Rules already exists, skipping")
    elif source_rules.exists():
        cursor_rules_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(source_rules), str(rules_dest))
        click.echo("  ✅ .cursor/rules/p8-enforcement.mdc (forces Agent to use MCP)")
    else:
        click.echo("  ⚠️  Cursor Rules template not found")

    click.echo(click.style("\n  🎉 P8 initialized!\n", fg="green", bold=True))
    click.echo("  Next steps:")
    click.echo(f"    cd {target_path.name}" if target != "." else "")
    click.echo("    p8 list                    # View SKILLs")
    click.echo("    p8 new my_custom_skill     # Create custom SKILL")
    click.echo("    p8 validate skills/example # Validate SKILL")
    click.echo("    p8 serve                   # Start MCP enforcement server")
    click.echo()


_MINIMAL_AGENTS_MD = """\
# AGENTS.md — P8 Global Instructions (all Agents must follow)

You are working in a project governed by Pattern 8 (P8). You must follow these rules.

## Core Constraints

Before starting any task: check `skills/` directory, read the matching SKILL.md, strictly follow pipeline steps.

## Five Patterns

1. **Pipeline** — Execute steps in order, no skipping
2. **Inversion** — Block and ask if info is incomplete
3. **Generator** — Output in template.yaml format
4. **Tool Wrapper** — Check security.yaml before executing
5. **Reviewer** — Self-audit after completion, roll back if non-compliant (up to 3 retries)

## Security Red Lines
Rules in `references/security.yaml` are absolute hard constraints that must never be violated.
"""


# ════════════════════════════════════════════════════════════
#  p8 mcp-config — Generate MCP config
# ════════════════════════════════════════════════════════════

@main.command("mcp-config")
@click.option("--client", "-c", default="claude",
              type=click.Choice(["claude", "cursor", "json"]),
              help="Target client")
def mcp_config(client: str):
    """
    Generate MCP client configuration.
    """
    import shutil as _shutil
    p8_path = _shutil.which("p8") or "p8"

    if client == "claude":
        config = {"mcpServers": {"pattern8": {"command": p8_path, "args": ["serve"]}}}
        click.echo(click.style("\n🎱 Claude Desktop MCP Config\n", fg="cyan", bold=True))
        click.echo("  Paste into:")
        click.echo("  ~/Library/Application Support/Claude/claude_desktop_config.json\n")
        click.echo(json.dumps(config, indent=2, ensure_ascii=False))
    elif client == "cursor":
        config = {"mcpServers": {"pattern8": {"command": p8_path, "args": ["serve"]}}}
        click.echo(click.style("\n🎱 Cursor MCP Config\n", fg="cyan", bold=True))
        click.echo("  Paste into:")
        click.echo("  .cursor/mcp.json (project) or ~/.cursor/mcp.json (global)\n")
        click.echo(json.dumps(config, indent=2, ensure_ascii=False))
    else:
        config = {"command": p8_path, "args": ["serve"], "name": "pattern8"}
        click.echo(json.dumps(config, indent=2, ensure_ascii=False))
    click.echo()


# ════════════════════════════════════════════════════════════
#  p8 serve — Start MCP enforcement server
# ════════════════════════════════════════════════════════════

@main.command()
def serve():
    """
    Start P8 MCP enforcement server.
    Agents call security checks and audits via MCP.

    Usage:
        p8 serve
    """
    import asyncio

    click.echo(click.style("\n🎱 P8 MCP Enforcement Server", fg="cyan", bold=True))
    click.echo("  Mode: stdio (MCP)")
    click.echo("  Resources: skill://index, skill://{name}/checklist, skill://{name}/template")
    click.echo("  Tools: submit_review, execute_tool")
    click.echo("  Press Ctrl+C to stop\n")

    try:
        from p8.enforcement.mcp_server import main as mcp_main
        asyncio.run(mcp_main())
    except ImportError:
        click.echo(click.style("❌ Enforcement module not installed", fg="red"))
        click.echo("   Run: pip install 'pattern8[enforcement]'")
        raise SystemExit(1)
    except KeyboardInterrupt:
        click.echo("\n👋 Server stopped.")


# ════════════════════════════════════════════════════════════
#  Entry
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
