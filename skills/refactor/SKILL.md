---
name: refactor
description: Constrains the Agent to follow a safe refactoring process — guarantee functional equivalence while improving code quality.
assets:
  checklist: assets/checklist.yaml
  template: assets/template.yaml
references:
  guidelines: references/guidelines.yaml
  security: references/security.yaml
---

# Code Refactor

Constrains the Agent to perform safe code refactoring: guarantee functional equivalence while improving code quality.

<PIPELINE>

## Step 1: Inversion (Requirements Alignment)

Before refactoring, you must check every item in `assets/checklist.yaml`.

<HARD-GATE>
If the user has not specified the refactoring goal (readability? performance? DRY?), you must ask first.
If you cannot confirm which behaviors must remain unchanged, you must block and ask.
Do NOT start refactoring without knowing what must NOT change.
</HARD-GATE>

## Step 2: Generator (Generate Refactoring Plan from Template)

Your output must strictly follow the format in `assets/template.yaml`.
Must include: refactoring goal, impact analysis, refactoring steps (with diff), behavioral equivalence checklist.

## Step 3: Tool Wrapper (Security Fence)

If you need to execute code during refactoring for verification, check `references/security.yaml` first.
Do not delete tests or remove error handling logic during refactoring.

## Step 4: Reviewer (Self-Audit Loop)

Audit your refactoring output against `references/guidelines.yaml`.
Key checks: is the behavior equivalent? Are public APIs unchanged? Is code complexity reduced?
Roll back and regenerate if non-compliant, up to 3 retries.

</PIPELINE>
