---
name: code_review
description: Constrains the Agent to perform structured code reviews across correctness, security, performance, and maintainability.
assets:
  checklist: assets/checklist.yaml
  template: assets/template.yaml
references:
  guidelines: references/guidelines.yaml
  security: references/security.yaml
---

# Code Review

Constrains the Agent to perform structured code reviews covering four dimensions: correctness, security, performance, and maintainability.

<PIPELINE>

## Step 1: Inversion (Requirements Alignment)

Before starting a review, you must check every item in `assets/checklist.yaml`.

<HARD-GATE>
If the user has not provided a code snippet or file path, you must block and ask. Do not guess.
If the programming language and framework cannot be confirmed, you must ask before starting.
Do NOT start reviewing until ALL checklist items are confirmed.
</HARD-GATE>

## Step 2: Generator (Generate Review Report from Template)

Your output must strictly follow the format defined in `assets/template.yaml`.
You must cover all four dimensions: correctness, security, performance, maintainability.
No section may be skipped.

## Step 3: Tool Wrapper (Security Fence)

If you need to execute code to verify issues, you must first check `references/security.yaml`.
Commands matching the blacklist (e.g., rm -rf, sudo) must be rejected immediately.

## Step 4: Reviewer (Self-Audit Loop)

After generating the review report, audit it against the criteria in `references/guidelines.yaml`.
If any criterion is not met (e.g., missing line numbers, no fix code), roll back and regenerate.
Up to 3 retries. If still non-compliant after 3 retries, inform the user which criteria failed.

</PIPELINE>
