# Pattern 8 (P8)

> 🎱 AI Agent Governance Framework

P8 constrains how AI Agents (Claude, Cursor, Gemini, etc.) behave in your project.
**Law (SKILL files) + Police (code engine) + Zero-Trust (Hook + Rules) = Agents can't jailbreak.**

## Architecture

```
Developer-editable (Law)              Read-only Engine (Police)
┌──────────────────────┐          ┌──────────────────────────┐
│ SKILL.md             │          │ SecurityGuard            │
│ checklist.yaml       │  read →  │  ↳ regex blacklist       │
│ template.yaml        │          │  ↳ path restrictions     │
│ guidelines.yaml      │          │ Reviewer                 │
│ security.yaml        │          │  ↳ static rule engine    │
│                      │          │  ↳ P8AuditError rollback │
│ "Constitution"       │          │ "Police"                 │
└──────────────────────┘          └──────────────────────────┘
                ↕ Agent calls via MCP ↕
```

### Three Defense Layers

| Layer | Method | Can Agent bypass? |
|-------|--------|:-:|
| Layer 1 | `AGENTS.md` + Cursor Rules prompt injection | ⚠️ Theoretically yes |
| Layer 2 | MCP Tools (`submit_review` / `execute_tool`) | ❌ Code-enforced |
| Layer 3 | Git pre-commit hook | ❌ Impossible to bypass |

### Progressive Disclosure (aligned with Google ADK)

Agent loads lightweight Resources on startup; audit rules are loaded internally on demand:

| Type | Interface | Visible to Agent? |
|------|-----------|:-:|
| Resource | `skill://index` — SKILL list | ✅ |
| Resource | `skill://{name}/checklist` — Entry checklist | ✅ |
| Resource | `skill://{name}/template` — Output template | ✅ |
| **Tool** | `submit_review` — Submit for audit | ✅ Interface visible |
| **Tool** | `execute_tool` — Request execution | ✅ Interface visible |
| 🔒 | `guidelines.yaml` — Audit rules | ❌ Loaded internally |
| 🔒 | `security.yaml` — Security red lines | ❌ Loaded internally |

## Installation

```bash
# Basic install (CLI + SKILL management)
pip install pattern8

# Full install (with MCP enforcement server)
pip install 'pattern8[enforcement]'
```

## Quick Start

```bash
# 1. Initialize P8 (auto-installs 5 components)
p8 init my-project
#   ✅ AGENTS.md              — Global agent instructions
#   ✅ skills/ (5 SKILLs)     — Built-in governance rules
#   ✅ .gitignore
#   ✅ .git/hooks/pre-commit   — Commit-time audit
#   ✅ .cursor/rules/          — Forces agent to use MCP

# 2. Manage SKILLs
p8 list                         # List all SKILLs
p8 new my_custom_skill          # Create custom SKILL
p8 validate skills/example      # Validate SKILL integrity

# 3. Start enforcement server
p8 serve                        # Start MCP enforcement server
p8 mcp-config --client cursor   # Generate Cursor MCP config
```

## Connect to Cursor

```bash
p8 mcp-config --client cursor
```

Paste the output into `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "pattern8": {
      "command": "p8",
      "args": ["serve"]
    }
  }
}
```

## 5 Patterns × 5 Built-in SKILLs

| Pattern | Controls | Config File |
|---------|----------|-------------|
| **Pipeline** | Step execution order | `SKILL.md` |
| **Inversion** | Blocks if info is missing, asks user | `checklist.yaml` |
| **Generator** | Output format constraints | `template.yaml` |
| **Tool Wrapper** | Dangerous command interception | `security.yaml` |
| **Reviewer** | Output quality audit | `guidelines.yaml` |

| SKILL | Use Case |
|-------|----------|
| `example` | PRD document generation |
| `code_review` | Code review (correctness / security / performance / maintainability) |
| `bug_fix` | Bug fixing (locate → root cause → fix → regression) |
| `refactor` | Code refactoring (functional equivalence guarantee) |
| `feature_dev` | Feature development (requirements → design → implement → verify) |

## SKILL Directory Structure

```
skills/code_review/
├── SKILL.md                   # Pipeline + <HARD-GATE> blockers
├── assets/
│   ├── checklist.yaml         # Inversion entry checklist
│   └── template.yaml          # Generator output template
└── references/
    ├── guidelines.yaml        # Reviewer audit rules (🔒 invisible to Agent)
    └── security.yaml          # Tool Wrapper security red lines (🔒 invisible to Agent)
```

## License

MIT
