---
name: example
description: Constrains the Agent to generate structured Product Requirements Documents (PRDs) with quality and completeness guarantees.
assets:
  checklist: assets/checklist.yaml
  template: assets/template.yaml
references:
  guidelines: references/guidelines.yaml
  security: references/security.yaml
---

# Product Requirements Document (PRD)

Constrains the Agent to follow a standard process for generating PRDs, ensuring completeness, format compliance, and security.

<PIPELINE>

## Step 1: Inversion (Requirements Alignment)

Before generating a PRD, you must check every item in `assets/checklist.yaml`.

<HARD-GATE>
If the user has not specified the target audience and core features, you must block and ask.
If technical constraints and non-functional requirements are unclear, you must ask before proceeding.
If success criteria and platform context are not specified, you must ask before proceeding.
Do NOT generate a PRD without knowing target users, core features, technical constraints, and platform context.
</HARD-GATE>

## Step 2: Generator (Generate PRD from Template)

Your output must strictly follow the PRD format defined in `assets/template.yaml`.
All sections (objectives, user personas, feature specs, technical constraints, etc.) must be filled.
No sections may be omitted or replaced with placeholders.

## Step 3: Tool Wrapper (Security Fence)

The PRD must not contain any content prohibited by `references/security.yaml`.
For example: no real user PII, no suggestions to store passwords in plain text.

## Step 4: Reviewer (Self-Audit Loop)

Audit the generated PRD against the criteria in `references/guidelines.yaml`.
If any criterion is not met, roll back and regenerate, up to 3 times.

</PIPELINE>
