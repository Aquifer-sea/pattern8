---
name: feature_dev
description: Constrains the Agent to follow a structured feature development process — requirements → design → implement → verify.
assets:
  checklist: assets/checklist.yaml
  template: assets/template.yaml
references:
  guidelines: references/guidelines.yaml
  security: references/security.yaml
---

# Feature Development

Constrains the Agent to follow "understand requirements → technical design → write code → self-test" structured process.

<PIPELINE>

## Step 1: Inversion (Requirements Alignment)

Before starting development, you must check every item in `assets/checklist.yaml`.

<HARD-GATE>
If the user has not provided acceptance criteria, you must block and ask.
If the tech stack is unclear, you must confirm before starting.
Do NOT start coding without acceptance criteria and tech stack confirmation.
</HARD-GATE>

## Step 2: Generator (Generate Development Plan + Code from Template)

Your output must strictly follow the format in `assets/template.yaml`.
Must include: requirement understanding, technical design, implementation code, test code, integration notes.

## Step 3: Tool Wrapper (Security Fence)

Commands executed during development must be checked against `references/security.yaml`.
Do not introduce dependencies with known vulnerabilities or bypass authentication mechanisms.

## Step 4: Reviewer (Self-Audit Loop)

Audit your development output against `references/guidelines.yaml`.
Key checks: does it match acceptance criteria? Are there tests? Is it backward compatible?
Roll back and regenerate if non-compliant, up to 3 retries.

</PIPELINE>
