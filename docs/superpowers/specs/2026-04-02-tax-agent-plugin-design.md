# Tax Agent Plugin — Design Spec

**Date:** 2026-04-02
**Author:** Fangyi Chen + Claude
**Status:** Approved

## Overview

A Claude Code marketplace plugin that guides users through federal tax filing: interactive interview, document import, tax calculation, IRS form PDF filling, and a self-evolving mechanism that improves the plugin from community usage.

## Plugin Structure

```
tax-agent/                             # plugin root
├── .claude-plugin/
│   └── plugin.json                    # marketplace manifest
├── package.json
├── forms/                             # bundled blank IRS fillable PDFs
│   ├── f1040-2025.pdf
│   ├── f1040sb-2025.pdf               # Schedule B
│   ├── f1040sd-2025.pdf               # Schedule D
│   └── f8949-2025.pdf                 # Form 8949
├── skills/
│   ├── tax-start/
│   │   └── SKILL.md
│   ├── tax-import/
│   │   └── SKILL.md
│   ├── tax-calculate/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── brackets-2025.md
│   │       └── credits-2025.md
│   ├── tax-fill/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── form-1040-fields.md
│   ├── tax-compare/
│   │   └── SKILL.md
│   ├── tax-evolve/
│   │   └── SKILL.md
│   ├── tax-publish/
│   │   └── SKILL.md
│   ├── tax-domain-rsu/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── rsu-tax-rules.md
│   ├── tax-domain-rental/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── schedule-e-rules.md
│   ├── tax-domain-harvest/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── wash-sale-rules.md
│   └── tax-domain-crypto/
│       ├── SKILL.md
│       └── references/
│           └── digital-asset-rules.md
├── data/                              # local only, gitignored
│   ├── tax-profile.json
│   ├── tax-calculation.json
│   ├── comparison-2025.json
│   ├── evolution-log.json
│   └── output/
│       └── 1040-2025.pdf
├── .gitignore
└── README.md
```

## .gitignore

```
data/
*.pdf
!forms/*.pdf
```

## Plugin Manifest

`.claude-plugin/plugin.json`:
```json
{
  "name": "tax-agent",
  "description": "AI tax filing assistant — interview, import documents, calculate, and fill IRS forms. Supports RSU, rental income, crypto, and tax-loss harvesting.",
  "version": "0.1.0",
  "author": "fangyic",
  "homepage": "",
  "repository": "",
  "license": "MIT",
  "keywords": ["tax", "1040", "irs", "filing", "w2", "1099"]
}
```

The `repository` field is read by `tax-evolve` and `tax-publish` to know where to submit PRs.

---

## Skills

### Core Pipeline

#### 1. `tax-start` — Interactive Interview

- **Invocation:** `/tax-start [year]`
- **Purpose:** Guide user through 6 sections to collect all tax data
- **Sections:** Personal info, dependents, income, deductions, credits, other
- **Resume:** Checks for existing `data/tax-profile.json` and offers to resume
- **Domain integration:** When income types are detected (e.g., user mentions rental income, RSU), invokes the corresponding `tax-domain-*` skill for specialized follow-up questions
- **Output:** `data/tax-profile.json`
- **Enhancement from current:** Add domain skill trigger conditions. Add more income types (Schedule C self-employment, Schedule E rental, HSA, student loan interest).

#### 2. `tax-import` — Document Parser

- **Invocation:** `/tax-import <file-path>`
- **Purpose:** Extract structured data from tax documents (PDF, image, text)
- **Supported documents (v1):** W2, 1099-B, 1099-DIV, 1099-INT, 1099-DA, 1099-MISC
- **Domain integration:** When RSU-related W2 box 14 codes or 1099-B ESPP lots detected, invokes `tax-domain-rsu`. When 1099-DA detected, invokes `tax-domain-crypto`.
- **Output:** Merges into `data/tax-profile.json`
- **Enhancement from current:** Expand beyond W2 to all 1099 types. Add domain skill triggers.

#### 3. `tax-calculate` — Tax Computation

- **Invocation:** `/tax-calculate`
- **Purpose:** Compute federal return from `data/tax-profile.json`
- **Steps:** Total income → AGI → deductions → taxable income → tax brackets → credits → refund/owed
- **References:** `brackets-2025.md` (tax brackets by filing status), `credits-2025.md` (credit rules, phase-outs, refundability)
- **Domain integration:** Reads domain-specific data from `tax-profile.json` (e.g., `domains.rental` for Schedule E calculations). Consults domain skill references for correct computation rules.
- **Output:** `data/tax-calculation.json`
- **Enhancement from current:** Extract bracket data and credit rules into reference files. Add Schedule B/D/E computation. Add qualified dividend tax worksheet.

#### 4. `tax-fill` — IRS PDF Form Filling

- **Invocation:** `/tax-fill`
- **Purpose:** Fill official IRS fillable 1040 PDF with calculated values
- **Prerequisites:** `data/tax-calculation.json` must exist
- **How it works:**
  1. Reads `data/tax-calculation.json`
  2. Generates an XFDF data file using the field mapping in `references/form-1040-fields.md`
  3. Uses `pdftk` to inject values: `pdftk forms/f1040-2025.pdf fill_form data.xfdf output data/output/1040-2025.pdf`
  4. Detects required schedules from calculation data and fills those too
- **Reference:** `form-1040-fields.md` maps calculation JSON keys → PDF form field names
- **Supported forms (v1):** Form 1040, Schedule B, Schedule D, Form 8949
- **Output:** `data/output/1040-2025.pdf` (and schedule PDFs)
- **Post-fill:** Suggests `/tax-compare` if user also filed with TurboTax

---

### Domain Reference Skills

All domain skills follow a consistent pattern:

```markdown
---
name: tax-domain-{name}
description: [domain] tax rules. Invoked by core skills when [trigger].
allowed-tools: [Read, Write, Edit, AskUserQuestion]
---

## Trigger Conditions
## Interview Questions
## Data Schema
## Calculation Rules
## References
```

#### 5. `tax-domain-rsu` — RSU / ESPP Income

- **Triggers:** W2 box 14 with RSU codes, 1099-B with ESPP/RSU lots
- **Interview:** Vesting schedule, grant date FMV, supplemental withholding rate, sale type (same-day, sell-to-cover, hold)
- **Data:** Stored under `domains.rsu` in tax-profile.json
- **Calculation:** Prevents double-counting of W2 income + 1099-B proceeds. Adjusts cost basis for RSU (basis = FMV at vest). Handles disqualifying dispositions for ESPP.
- **Reference:** `rsu-tax-rules.md`

#### 6. `tax-domain-rental` — Rental Property

- **Triggers:** User reports rental income during interview
- **Interview:** Property address, days rented vs personal use, rental income, expenses (mortgage interest, property tax, insurance, repairs, depreciation, HOA, utilities, property management)
- **Data:** Stored under `domains.rental[]` in tax-profile.json (array for multiple properties)
- **Calculation:** Schedule E Part I. Passive activity loss rules. Depreciation (27.5 year straight-line for residential). $25,000 rental loss allowance with AGI phase-out.
- **Reference:** `schedule-e-rules.md`

#### 7. `tax-domain-harvest` — Tax-Loss Harvesting

- **Triggers:** 1099-B contains wash sale adjustments, or unrealized losses detected
- **Interview:** Confirms wash sale lots, asks about substantially identical securities purchased within 30-day window
- **Data:** Stored under `domains.harvest` in tax-profile.json
- **Calculation:** Adjusts basis for wash sale disallowed losses. $3,000 net capital loss deduction limit. Carryforward tracking.
- **Reference:** `wash-sale-rules.md`

#### 8. `tax-domain-crypto` — Digital Assets

- **Triggers:** 1099-DA detected during import
- **Interview:** Cost basis method (FIFO, specific ID), stablecoin transactions, DeFi income, mining/staking income
- **Data:** Stored under `domains.crypto` in tax-profile.json
- **Calculation:** Form 8949 Box H (noncovered). Stablecoin aggregation rules. "Yes" checkbox on Form 1040 page 1.
- **Reference:** `digital-asset-rules.md`

---

### Self-Evolution Skills

#### 9. `tax-compare` — Diff Two Returns

- **Invocation:** `/tax-compare <our-pdf> <reference-pdf>`
- **Purpose:** Compare plugin's output against TurboTax (or other software) output
- **How it works:**
  1. Reads both PDFs, extracts values by 1040 line item
  2. Produces line-by-line diff with match/mismatch indicators
  3. For each discrepancy, traces back to which calculation step or data source caused it
  4. Saves structured diff to `data/comparison-2025.json`
  5. Asks: "Would you like to help improve this tax agent for the community?"
- **Output:** `data/comparison-2025.json`, on-screen diff summary

#### 10. `tax-evolve` — Analyze & Generate Fixes

- **Invocation:** `/tax-evolve`
- **Prerequisites:** `data/comparison-2025.json` must exist
- **How it works:**
  1. Reads the comparison diff
  2. Classifies each discrepancy:
     - **Calculation error** — formula is wrong → edits to `tax-calculate` or its references
     - **Missing data** — interview never asked → new questions for `tax-start`
     - **Missing domain** — unsupported income/deduction type → proposes new `tax-domain-*` skill scaffold
  3. Generates the actual file changes (skill edits, new skills, reference updates)
  4. Logs to `data/evolution-log.json` for pattern detection across runs
  5. Invokes `/tax-publish` to submit PR
- **Pattern detection:** If `evolution-log.json` shows the same gap appearing multiple times, prioritizes proposing a new domain skill rather than one-off fixes
- **Privacy:** NEVER includes user tax numbers in generated changes. Only includes which lines differed (by direction/percentage) and the rule fix.

#### 11. `tax-publish` — Git Push & PR

- **Invocation:** `/tax-publish [description]`
- **Purpose:** Create branch, commit skill changes, push, and open PR
- **How it works:**
  1. Reads `repository` from `.claude-plugin/plugin.json`
  2. Creates branch: `evolve/{description}-{date}` (from tax-evolve) or `contrib/{description}-{date}` (from user)
  3. Stages only skill files and references (enforces: never `data/`, never user PDFs)
  4. Commits with structured message including what changed and why
  5. Pushes with `-u` flag
  6. Opens PR via `gh pr create` with:
     - Summary of changes
     - Root cause (if from tax-evolve)
     - Evidence (anonymized line-item deltas, no PII)
  7. Shows PR URL to user
- **Safety:** Shows full diff to user for review before pushing. User can redact anything.

---

## Data Contracts

### `data/tax-profile.json`

Single source of truth for all collected data. Schema:

```json
{
  "taxYear": 2025,
  "personalInfo": { ... },
  "dependents": [ ... ],
  "income": {
    "w2s": [ ... ],
    "otherIncome": [ ... ]
  },
  "deductions": { ... },
  "credits": { ... },
  "other": { ... },
  "domains": {
    "rsu": { ... },
    "rental": [ ... ],
    "harvest": { ... },
    "crypto": { ... }
  },
  "interviewStatus": { ... }
}
```

### `data/tax-calculation.json`

Full audit trail of computation with all intermediate values.

### `data/comparison-2025.json`

Line-by-line diff between plugin output and reference return.

### `data/evolution-log.json`

Tracks discrepancies across runs for pattern detection:

```json
{
  "entries": [
    {
      "date": "2026-04-02",
      "lines": [
        { "line": 19, "description": "CTC", "delta": 352, "classification": "calculation_error", "resolved": true }
      ]
    }
  ]
}
```

---

## Data Flow

```
/tax-start ──► /tax-import ──► /tax-calculate ──► /tax-fill
    │              │                │                  │
    │         tax-domain-*     tax-domain-*            │
    │         (as needed)      (references)            │
    ▼              ▼                ▼                  ▼
tax-profile.json  (merges)   tax-calculation.json   1040.pdf
                                                      │
                                              /tax-compare ◄── turbotax.pdf
                                                      │
                                                      ▼
                                              comparison.json
                                                      │
                                               /tax-evolve
                                                      │
                                                      ▼
                                              skill changes
                                                      │
                                              /tax-publish
                                                      │
                                                      ▼
                                                GitHub PR
```

Skills communicate through files, not shared state. Each skill reads from `data/` and writes back. Users can re-run any step independently.

---

## What Gets Published vs. Local

| Published (in repo) | Local only (gitignored) |
|---------------------|------------------------|
| All `skills/*/SKILL.md` | `data/` (all user data) |
| All `skills/*/references/` | User-provided PDFs |
| `.claude-plugin/` | `data/output/` (generated forms) |
| `package.json` | `data/evolution-log.json` |
| `forms/*.pdf` (blank IRS forms) | |
| `README.md` | |

---

## Implementation Priority

1. **Restructure** — convert current skills to plugin format, extract references
2. **`tax-fill`** — PDF form filling to complete the core pipeline
3. **Domain skills** — `tax-domain-rsu`, `tax-domain-rental`, `tax-domain-harvest`, `tax-domain-crypto`
4. **`tax-compare`** — PDF diff engine
5. **`tax-evolve`** — analysis and fix generation
6. **`tax-publish`** — git/PR workflow

---

## Limitations (v1)

- Federal return only (no state returns)
- 2025 tax year only (bracket/credit data hardcoded to 2025)
- Form 1040 + Schedule B + Schedule D + Form 8949 only
- No e-filing (print and mail)
- EIC amounts estimated (need exact IRS tables)
- No AMT calculation
- No Schedule C (self-employment) — future domain skill
