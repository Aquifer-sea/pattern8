# Contributing Guide

Thank you for your interest in Pattern 8! Here's how to contribute.

## Development Setup

```bash
git clone https://github.com/pattern8/p8.git
cd p8
python3.12 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest tests/ -v
```

## Project Structure

```
src/p8/
├── cli.py                    # CLI entry (init/list/validate/new/serve/mcp-config)
└── enforcement/              # Enforcement module (code-level enforcement)
    ├── security_guard.py     # Tool Wrapper police (regex blacklist + path blocking)
    ├── reviewer.py           # Reviewer police (static rule audit engine)
    └── mcp_server.py         # MCP enforcement interface (3 Resources + 2 Tools)

skills/                       # Law files (developer-customizable)
├── example/                  # Example SKILL (PRD generation)
├── code_review/              # Code review constraints
├── bug_fix/                  # Bug fix constraints
├── refactor/                 # Refactoring constraints
└── feature_dev/              # Feature development constraints

AGENTS.md                     # Global agent instructions
```

## Adding a New SKILL

```bash
p8 new my_skill
# Then edit the files under skills/my_skill/
```

## Code Standards

- All code should have English comments
- New features must have corresponding tests
- Follow existing naming conventions

## Commit Convention

```
feat: new feature
fix: bug fix
docs: documentation update
test: testing
refactor: refactoring
```
