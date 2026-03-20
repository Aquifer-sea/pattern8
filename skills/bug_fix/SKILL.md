---
name: bug_fix
description: Constrains the Agent to follow a structured bug fix process — locate → root cause → fix → regression verify.
assets:
  checklist: assets/checklist.yaml
  template: assets/template.yaml
references:
  guidelines: references/guidelines.yaml
  security: references/security.yaml
---

# Bug Fix

Constrains the Agent to follow the "locate → root cause analysis → fix → regression verification" structured process.

<PIPELINE>

## Step 1: Inversion (Requirements Alignment)

Before fixing a bug, you must check every item in `assets/checklist.yaml`.

<HARD-GATE>
If the user has not provided an error message or reproduction steps, you must block and ask.
Do NOT start fixing until the bug is clearly described and reproducible.
</HARD-GATE>

## Step 2: Generator (Generate Fix Report from Template)

Your output must strictly follow the format defined in `assets/template.yaml`.
Must include: root cause analysis, fix plan, fix code (diff format), impact analysis, regression checklist.
Vague suggestions like "try changing this" are not allowed.

## Step 3: Tool Wrapper (Security Fence)

If you need to execute commands to reproduce or verify a bug, check `references/security.yaml` first.
Do not execute any high-risk commands that could damage existing code or environment.

## Step 4: Reviewer (Self-Audit Loop)

After fixing, audit your fix against `references/guidelines.yaml`.
Key checks: does the fix address the root cause? Does it introduce new bugs? Is the diff minimal?
Roll back and regenerate if non-compliant, up to 3 retries.

</PIPELINE>
