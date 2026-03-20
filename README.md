<div align="center">

# Pattern 8 (P8)

**Zero-Trust Governance Framework to stop AI Agents from hallucinating, breaking things, and bypassing your rules.**
<br/>

> *"Your prompt is merely a suggestion. P8 is the law."*

[![PyPI version](https://img.shields.io/pypi/v/pattern8?color=blue&style=for-the-badge)](https://pypi.org/project/pattern8/)
[![Python](https://img.shields.io/pypi/pyversions/pattern8?style=for-the-badge)](https://pypi.org/project/pattern8/)
[![CI](https://github.com/Aquifer-sea/pattern8/actions/workflows/ci.yml/badge.svg?style=for-the-badge)](https://github.com/Aquifer-sea/pattern8/actions)
[![Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen.svg?style=for-the-badge)](https://github.com/Aquifer-sea/pattern8/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**[ 📚 Read the Docs](#) • [ 💬 Join Discord ](#) • [ 🐦 Twitter ](#)**
</div>

<div align="center">
  <img src="https://via.placeholder.com/800x400/000000/FFFFFF/?text=[+PLACEHOLDER+FOR+KILLER+DEMO+GIF+]" alt="P8 intercepts dangerous agent command" width="100%" />
</div>

---

## The Chaos vs. The Law

Are you tired of AI coding agents (Claude, Cursor, Devin) ignoring your instructions, deleting the wrong files, or pushing code without tests? 

Prompts are not enough. **Prompt injection defence is impossible.** To truly control an agent, constraints must be enforced at the OS and code level.

### ❌ Without P8 (The Chaos)
- **Agent decides** to skip writing tests because it's "too trivial".
- **Agent runs** `rm -rf` by mistake during a multi-step refactor.
- **Agent outputs** a feature without ever writing a design doc.
- **Agent ignores** your 5,000-word system prompt because its context window is full.

### 🛡️ With P8 (The Law)
- **MCP SecurityGuard** intercepts and blocks dangerous commands at the OS level.
- **MCP Reviewer** forces the agent into a strict retry-loop if output doesn't match the `template.yaml`.
- **Pre-commit Hooks** ensure the agent hasn't tampered with the rules themselves.
- **Inversion Pattern** forces the agent to stop and ask you clarifying questions instead of hallucinating.

---

## ⚡ Zero to Hero in 30 Seconds

Take absolute control of your codebase with 3 commands:

```bash
# 1. Install the enforcer (Python 3.8+)
pip install pattern8

# 2. Add handcuffs to your current project
p8 init

# 3. Done. Your Agents are now under control.
p8 list
```

---

## 🚔 How It Works: Law vs. Police

P8 separates **Law** (editable rules) from **Police** (read-only execution engine):

```text
Developer-editable (Law)              Read-only Engine (Police)
┌──────────────────────┐          ┌──────────────────────────┐
│ SKILL.md             │          │ SecurityGuard            │
│ checklist.yaml       │  read →  │  ↳ regex blacklist       │
│ template.yaml        │          │  ↳ OS command hooks      │
│ guidelines.yaml  🔒  │          │ Reviewer                 │
│ security.yaml    🔒  │          │  ↳ static rule engine    │
│                      │          │  ↳ P8AuditError rollback │
│ "The Constitution"   │          │ "The Police"             │
└──────────────────────┘          └──────────────────────────┘
                ↕ Agent calls via MCP ↕
```

You write the **Law** in simple Markdown and YAML. The **Police** engine enforces them automatically via MCP (Model Context Protocol). Files marked with 🔒 are deliberately hidden from the Agent so it cannot read the security parameters used to audit it.

---

## 💎 The 5 Golden SKILLs

P8 comes with 5 industrial-grade developer SKILLs out of the box. *Don't just code. Engineer.*

### 📝 PRD (`skills/prd/`)
*Don't just build. Think first.* 
Forces the agent to gather requirements and generate a structured Product Requirements Document before writing a single line of logic.

### 🐛 Bug Fix (`skills/bug_fix/`)
*Find the root cause, or don't fix it at all.* 
Forces the agent through a strict 4-step golden path: Reproduce → Root Cause Analysis → Fix → Regression Test. 

### 🔒 Code Review (`skills/code_review/`)
*Never merge unreviewed AI slop.* 
The agent must submit its changes to the `Reviewer` engine. If the code fails security, performance, or correctness guidelines, the engine throws a `P8_AUDIT_FAILED` error, forcing the agent to retry and fix its own mess (up to 3 times) before presenting it to you.

### 🏗️ Refactor (`skills/refactor/`)
*Change structure, not behavior.* 
Forces the agent to guarantee functional equivalence test-passes after moving code around.

### 🚀 Feature Dev (`skills/feature_dev/`)
*End-to-end delivery.*
Requirements → Technical Design → Implementation → Unit Tests.

---

## 🛠️ CLI Reference

```bash
p8 init [target]                # Initialize P8 and generate the 5 default SKILLs
p8 list                         # List all available SKILLs in the current project
p8 validate <skill_path>        # Validate SKILL file integrity (run after editing)
p8 new <skill_name>             # Create a scaffold for a new custom SKILL
```

---

## 🔌 Connect to Cursor / Windsurf / Claude Desktop

To turn on the active "Police" enforcement engine, install the MCP extension:

```bash
# Full install with MCP server support
pip install 'pattern8[enforcement]'

# Generate MCP config for Cursor
p8 mcp-config --client cursor
```

Paste the output into `.cursor/mcp.json`. Now, every time the Cursor Agent tries to run a command or finish a task, it **must** pass through the P8 `execute_tool` and `submit_review` checkpoints. 

---

## 🤝 Contributing

We welcome completely new SKILLs! See [CONTRIBUTING.md](CONTRIBUTING.md) for architectural details and how to open a PR.

## 📄 License

MIT
