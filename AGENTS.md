# AGENTS.md — P8 Global Instructions (all Agents must follow)

# Pattern 8 (P8) — Agent Behavior Constraints

You are working in a project governed by the Pattern 8 (P8) framework. You must follow these rules.

## Core Constraints

Before starting any task, you must:

1. **Check the `skills/` directory** to find a SKILL matching the current task
2. **Read all files in that SKILL** (SKILL.md + assets/ + references/)
3. **Strictly follow the pipeline steps** described in SKILL.md

## Five Patterns (cannot be skipped)

### 1. Pipeline
Tasks must be executed in the order defined in SKILL.md. No steps may be skipped.

### 2. Inversion
Before starting work, check every item in `assets/checklist.yaml`.
If the user's request is missing required information, you must **stop and ask**, not guess.

### 3. Generator
Output must strictly follow the format defined in `assets/template.yaml`.
No freestyle — every template field must be filled.

### 4. Tool Wrapper
Before executing any tool call, check `references/security.yaml`.
Operations that hit the blacklist or violate security rules must be rejected immediately.

### 5. Reviewer
After completing output, self-audit using the criteria in `references/guidelines.yaml`.
If non-compliant, roll back and regenerate, up to 3 retries.
If still non-compliant after 3 retries, inform the user and explain why.

## Security Red Lines

Rules in `references/security.yaml` are **absolute hard constraints that must never be violated**.
Violating any security red line requires you to:
1. Immediately stop the current operation
2. Report the violation to the user
3. Do NOT attempt to bypass or work around it

## SKILL Priority

If a matching SKILL is found, you must use it.
If no matching SKILL exists, work normally but still follow the spirit of the five patterns.
