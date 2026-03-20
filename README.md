# Pattern 8 (P8)

> 🎱 AI Agent Governance Framework

P8 constrains how AI Agents (Claude, Cursor, Gemini, etc.) behave in your project.
**Law (SKILL files) + Police (code engine) + Zero-Trust (Hook + Rules) = Agents can't jailbreak.**

---

## Installation

```bash
pip install pattern8
```

## Quick Start (3 commands)

```bash
# 1. Create a project and initialize P8
mkdir my-project && cd my-project
git init
p8 init

# 2. View installed SKILLs
p8 list

# 3. Validate SKILL integrity
p8 validate skills/code_review
```

After running `p8 init`, your project will have:

```
my-project/
├── AGENTS.md                          # Global rules all Agents must follow
├── skills/                            # 5 built-in governance SKILLs
│   ├── example/                       # PRD document generation
│   ├── code_review/                   # Code review enforcement
│   ├── bug_fix/                       # Bug fix process enforcement
│   ├── feature_dev/                   # Feature development enforcement
│   └── refactor/                      # Refactoring enforcement
├── .cursor/rules/p8-enforcement.mdc   # Forces Cursor Agent to use MCP
└── .git/hooks/pre-commit              # Audits every commit automatically
```

---

## How It Works

P8 separates **Law** (editable SKILL files) from **Police** (read-only Python engine):

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

You edit the **Law** files to define constraints. The **Police** engine enforces them automatically.

---

## File-by-File Guide

### Files in Your Project Root

| File | What It Does | Who Edits It |
|------|-------------|:------------:|
| `AGENTS.md` | Global instructions every AI Agent must read before starting any task. Defines the 5 Patterns and security red lines. | You |
| `.cursor/rules/p8-enforcement.mdc` | Forces Cursor IDE Agent to call MCP tools for security checks. Without this, Agent can ignore rules. | Rarely |
| `.git/hooks/pre-commit` | Runs automatically on every `git commit`. Checks that SKILL files haven't been tampered with. | Never |

### Files Inside Each SKILL

Every SKILL (e.g. `skills/code_review/`) has 5 files:

```
skills/code_review/
├── SKILL.md                    ← Pipeline definition
├── assets/
│   ├── checklist.yaml          ← Entry requirements
│   └── template.yaml           ← Output format
└── references/
    ├── guidelines.yaml         ← Audit rules (🔒 invisible to Agent)
    └── security.yaml           ← Security red lines (🔒 invisible to Agent)
```

#### `SKILL.md` — Pipeline Definition

Defines the step-by-step process the Agent must follow. Contains:
- **`<PIPELINE>`** — Ordered steps (Agent cannot skip any)
- **`<HARD-GATE>`** — Blocking conditions (Agent must stop and ask if info is missing)

```markdown
## Step 1: Inversion — Check checklist.yaml, block if incomplete
## Step 2: Generator — Output in template.yaml format
## Step 3: Tool Wrapper — Check security.yaml before any tool call
## Step 4: Reviewer — Self-audit against guidelines.yaml
```

#### `checklist.yaml` — Entry Requirements

Agent must verify ALL items before starting. If any item is missing, Agent **stops and asks the user** instead of guessing.

```yaml
checklist:
  - "Target file or module path provided"
  - "Specific review focus described (security / performance / correctness)"
  - "Context or recent changes explained"
```

#### `template.yaml` — Output Format

Agent must output in exactly this structure. No freestyle.

```yaml
template: |
  # Code Review Report
  ## 1. Summary
  ## 2. Issues Found
  ## 3. Recommendations
```

#### `guidelines.yaml` — Audit Rules (🔒 Hidden from Agent)

The Agent **cannot see** these rules. The engine loads them internally to audit the Agent's output. If the output doesn't meet these criteria, it gets rejected and the Agent must retry (up to 3 times).

```yaml
guidelines:
  - "Every issue must have a specific line number"
  - "Must include severity level (HIGH / MEDIUM / LOW)"
  - "Must provide a concrete fix suggestion, not vague advice"
```

#### `security.yaml` — Security Red Lines (🔒 Hidden from Agent)

Hard security constraints. The Agent **cannot see** these rules. The engine blocks any operation that violates them.

```yaml
security:
  - "Never execute rm -rf, sudo, or curl|sh"
  - "Never modify files outside the project directory"
  - "Never commit credentials or API keys"
```

---

## The 5 Patterns

| # | Pattern | What It Does | Enforced By |
|:-:|---------|-------------|-------------|
| 1 | **Pipeline** | Agent must follow steps in order, no skipping | `SKILL.md` |
| 2 | **Inversion** | Agent blocks and asks if required info is missing | `checklist.yaml` |
| 3 | **Generator** | Agent outputs in strict template format | `template.yaml` |
| 4 | **Tool Wrapper** | Dangerous commands are intercepted | `security.yaml` |
| 5 | **Reviewer** | Agent self-audits, retries if non-compliant (up to 3×) | `guidelines.yaml` |

## 5 Built-in SKILLs

| SKILL | Use Case | What Agent Does |
|-------|----------|----------------|
| `example` | PRD generation | Gathers requirements → generates structured PRD |
| `code_review` | Code review | Reads code → finds issues → reports with line numbers |
| `bug_fix` | Bug fixing | Reproduces → root cause → fix → regression test |
| `refactor` | Refactoring | Analyzes → refactors → verifies functional equivalence |
| `feature_dev` | Feature development | Requirements → design → implement → verify |

---

## Three Defense Layers

| Layer | Method | Can Agent Bypass? |
|:-----:|--------|:-:|
| 1 | `AGENTS.md` + Cursor Rules — prompt injection | ⚠️ Theoretically yes |
| 2 | MCP Tools (`submit_review` / `execute_tool`) — code-level | ❌ No |
| 3 | Git pre-commit hook — OS-level | ❌ Impossible |

---

## CLI Commands

```bash
p8 init [target]                # Initialize P8 in a project
p8 list                         # List all available SKILLs
p8 validate <skill_path>        # Validate SKILL file integrity
p8 new <skill_name>             # Create a new custom SKILL
p8 serve                        # Start MCP enforcement server
p8 mcp-config --client cursor   # Generate MCP config for Cursor
```

## Create Your Own SKILL

```bash
p8 new my_custom_skill
```

This generates a scaffold at `skills/my_custom_skill/` with all 5 files. Edit them to define your own Agent constraints.

## Connect to Cursor (MCP)

```bash
# Full install with MCP server
pip install 'pattern8[enforcement]'

# Generate config
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

Now Cursor Agent will call `submit_review` and `execute_tool` through MCP, and the engine enforces security + audit automatically.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, project structure, and how to add new SKILLs.

## License

MIT
