# Plan 1: Plugin Restructure + tax-fill Implementation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the tax agent from loose skills into a proper Claude Code marketplace plugin structure, enhance existing skills with domain integration hooks, extract reference data, and implement `tax-fill` to generate mail-ready IRS 1040 PDFs.

**Architecture:** Flat skill namespace under `skills/` directory with `.claude-plugin/` manifest. Existing skills move from `.claude/skills/` to `skills/`. `tax-fill` uses Python `pypdf` to inject values into official IRS fillable PDFs via a field-mapping reference file. All skills communicate through JSON files in `data/`.

**Tech Stack:** Claude Code skills (Markdown), Python 3.11 + pypdf (PDF filling), Git + GitHub CLI (publishing)

**Spec:** `docs/superpowers/specs/2026-04-02-tax-agent-plugin-design.md`

---

### Task 1: Initialize Git Repo and Plugin Scaffold

**Files:**
- Create: `.git/` (via git init)
- Create: `.claude-plugin/plugin.json`
- Create: `package.json`
- Create: `.gitignore`
- Create: `README.md`

- [ ] **Step 1: Initialize git repository**

```bash
cd /Users/fangyic/ClaudeProjects/taxAgent
git init
```

Expected: `Initialized empty Git repository`

- [ ] **Step 2: Create `.claude-plugin/plugin.json`**

```bash
mkdir -p .claude-plugin
```

Write to `.claude-plugin/plugin.json`:

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

- [ ] **Step 3: Create `package.json`**

Write to `package.json`:

```json
{
  "name": "tax-agent",
  "version": "0.1.0",
  "type": "module",
  "description": "AI tax filing assistant for Claude Code"
}
```

- [ ] **Step 4: Create `.gitignore`**

Write to `.gitignore`:

```
data/
*.pdf
!forms/*.pdf
node_modules/
.DS_Store
__pycache__/
*.pyc
```

- [ ] **Step 5: Create `README.md`**

Write to `README.md`:

```markdown
# Tax Agent

AI-powered tax filing assistant for Claude Code. Guides you through an interactive interview, imports tax documents (W2, 1099), calculates your federal return, and generates a mail-ready IRS Form 1040 PDF.

## Skills

| Command | Description |
|---------|-------------|
| `/tax-start` | Start the interactive tax filing interview |
| `/tax-import <file>` | Import a W2, 1099, or brokerage statement |
| `/tax-calculate` | Calculate your federal tax return |
| `/tax-fill` | Generate a completed IRS Form 1040 PDF |

## Installation

Install as a Claude Code plugin from the marketplace, or clone locally:

```bash
git clone <repo-url>
cd tax-agent
```

## Privacy

All data stays local on your machine. Nothing is sent to any external service.

## License

MIT
```

- [ ] **Step 6: Commit scaffold**

```bash
git add .claude-plugin/ package.json .gitignore README.md
git commit -m "feat: initialize plugin scaffold with manifest and metadata"
```

---

### Task 2: Move Existing Skills to Plugin Structure

**Files:**
- Move: `.claude/skills/tax-start/SKILL.md` → `skills/tax-start/SKILL.md`
- Move: `.claude/skills/tax-import/SKILL.md` → `skills/tax-import/SKILL.md`
- Move: `.claude/skills/tax-calculate/SKILL.md` → `skills/tax-calculate/SKILL.md`

- [ ] **Step 1: Create plugin skills directory and copy skills**

```bash
mkdir -p skills/tax-start skills/tax-import skills/tax-calculate
cp .claude/skills/tax-start/SKILL.md skills/tax-start/SKILL.md
cp .claude/skills/tax-import/SKILL.md skills/tax-import/SKILL.md
cp .claude/skills/tax-calculate/SKILL.md skills/tax-calculate/SKILL.md
```

- [ ] **Step 2: Symlink for local development**

During development, we need skills discoverable from both locations. Create symlinks from `.claude/skills/` to `skills/` so the plugin structure is the source of truth but local Claude Code still finds them:

```bash
rm -rf .claude/skills/tax-start .claude/skills/tax-import .claude/skills/tax-calculate
ln -s ../../skills/tax-start .claude/skills/tax-start
ln -s ../../skills/tax-import .claude/skills/tax-import
ln -s ../../skills/tax-calculate .claude/skills/tax-calculate
```

Verify symlinks work:

```bash
ls -la .claude/skills/
cat .claude/skills/tax-start/SKILL.md | head -5
```

Expected: symlinks pointing to `../../skills/tax-*`, and SKILL.md content visible.

- [ ] **Step 3: Commit move**

```bash
git add skills/ .claude/skills/
git commit -m "refactor: move skills to plugin structure with symlinks for local dev"
```

---

### Task 3: Extract tax-calculate Reference Files

**Files:**
- Create: `skills/tax-calculate/references/brackets-2025.md`
- Create: `skills/tax-calculate/references/credits-2025.md`
- Modify: `skills/tax-calculate/SKILL.md`

- [ ] **Step 1: Create brackets reference**

```bash
mkdir -p skills/tax-calculate/references
```

Write to `skills/tax-calculate/references/brackets-2025.md`:

```markdown
# 2025 Federal Income Tax Brackets

## Single

| Rate | Income Range | Tax on Lower Brackets |
|------|-------------|----------------------|
| 10% | $0 – $11,925 | $0 |
| 12% | $11,926 – $48,475 | $1,192.50 |
| 22% | $48,476 – $103,350 | $5,578.50 |
| 24% | $103,351 – $197,300 | $17,651.00 |
| 32% | $197,301 – $250,525 | $40,199.00 |
| 35% | $250,526 – $626,350 | $57,231.00 |
| 37% | Over $626,350 | $188,769.75 |

## Married Filing Jointly

| Rate | Income Range | Tax on Lower Brackets |
|------|-------------|----------------------|
| 10% | $0 – $23,850 | $0 |
| 12% | $23,851 – $96,950 | $2,385.00 |
| 22% | $96,951 – $206,700 | $11,157.00 |
| 24% | $206,701 – $394,600 | $35,302.00 |
| 32% | $394,601 – $501,050 | $80,398.00 |
| 35% | $501,051 – $751,600 | $114,462.00 |
| 37% | Over $751,600 | $202,154.50 |

## Married Filing Separately

| Rate | Income Range | Tax on Lower Brackets |
|------|-------------|----------------------|
| 10% | $0 – $11,925 | $0 |
| 12% | $11,926 – $48,475 | $1,192.50 |
| 22% | $48,476 – $103,350 | $5,578.50 |
| 24% | $103,351 – $197,300 | $17,651.00 |
| 32% | $197,301 – $250,525 | $40,199.00 |
| 35% | $250,526 – $375,800 | $57,231.00 |
| 37% | Over $375,800 | $101,077.25 |

## Head of Household

| Rate | Income Range | Tax on Lower Brackets |
|------|-------------|----------------------|
| 10% | $0 – $17,000 | $0 |
| 12% | $17,001 – $64,850 | $1,700.00 |
| 22% | $64,851 – $103,350 | $7,442.00 |
| 24% | $103,351 – $197,300 | $15,912.00 |
| 32% | $197,301 – $250,500 | $38,460.00 |
| 35% | $250,501 – $626,350 | $55,484.00 |
| 37% | Over $626,350 | $187,031.50 |

## Qualified Dividends and Long-Term Capital Gains

| Rate | Single | MFJ | HoH |
|------|--------|-----|-----|
| 0% | $0 – $48,350 | $0 – $96,700 | $0 – $64,750 |
| 15% | $48,351 – $533,400 | $96,701 – $600,050 | $64,751 – $566,700 |
| 20% | Over $533,400 | Over $600,050 | Over $566,700 |

## Standard Deduction

| Filing Status | Amount |
|--------------|--------|
| Single | $15,000 |
| Married Filing Jointly | $30,000 |
| Married Filing Separately | $15,000 |
| Head of Household | $22,500 |

## Additional Standard Deduction (Age 65+ or Blind)

| Filing Status | Per qualifying condition |
|--------------|------------------------|
| Single / HoH | $2,000 |
| Married (either) | $1,600 |
```

- [ ] **Step 2: Create credits reference**

Write to `skills/tax-calculate/references/credits-2025.md`:

```markdown
# 2025 Federal Tax Credits Reference

## Child Tax Credit (CTC)

- **Amount:** $2,000 per qualifying child under 17 at end of tax year
- **Nonrefundable:** Limited to tax liability
- **Additional Child Tax Credit (ACTC) — refundable portion:**
  - Maximum refundable: $1,700 per child
  - Formula: 15% × (earned income - $2,500)
  - Capped at lesser of: unused CTC, or $1,700 per child
- **Phase-out:** Begins at AGI $400,000 (MFJ) / $200,000 (all others)
  - Reduces by $50 per $1,000 over threshold

## Earned Income Credit (EIC)

### Credit Parameters by Number of Qualifying Children (MFJ)

| Children | Credit Rate | Earned Income Threshold | Max Credit | Phase-out Begins | Phase-out Rate | Phase-out Ends |
|----------|------------|------------------------|------------|-----------------|---------------|----------------|
| 0 | 7.65% | $7,840 | $600 | $16,480 | 7.65% | $24,310 |
| 1 | 34% | $12,000 | $4,080 | $28,120 | 15.98% | $53,640 |
| 2 | 40% | $16,830 | $6,732 | $28,120 | 21.06% | $60,080 |
| 3+ | 45% | $16,830 | $7,574 | $28,120 | 21.06% | $64,060 |

### Single / HoH Phase-out Begins

| Children | Phase-out Begins |
|----------|-----------------|
| 0 | $10,330 |
| 1 | $21,980 |
| 2 | $21,980 |
| 3+ | $21,980 |

### Investment Income Limit
- Disqualified if investment income exceeds $11,600

### EIC Calculation
1. Compute credit = credit_rate × min(earned_income, earned_income_threshold)
2. If AGI > phase-out_begins: reduction = phase-out_rate × (AGI - phase-out_begins)
3. EIC = max(0, credit - reduction)

## Foreign Tax Credit

- Claim as credit (Form 1116) or deduction (Schedule A)
- Nonrefundable — limited to tax liability
- Unused credit can carry back 1 year or forward 10 years
- For amounts ≤ $300 single / $600 MFJ: can claim directly on 1040 without Form 1116

## Education Credits

### American Opportunity Credit (AOTC)
- Up to $2,500 per eligible student (first 4 years of higher education)
- 100% of first $2,000 + 25% of next $2,000
- 40% refundable (up to $1,000)
- Phase-out: $80,000–$90,000 single / $160,000–$180,000 MFJ

### Lifetime Learning Credit (LLC)
- Up to $2,000 per return (20% of first $10,000 expenses)
- Nonrefundable
- Phase-out: $80,000–$90,000 single / $160,000–$180,000 MFJ
```

- [ ] **Step 3: Update tax-calculate SKILL.md to reference external files**

Replace the full content of `skills/tax-calculate/SKILL.md` with:

```markdown
---
name: tax-calculate
description: Calculate federal tax return based on collected data. Use when the user wants to calculate taxes, see their refund, or compute what they owe.
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# Tax Calculation

You are a tax calculator. Compute the user's federal tax return based on data in `data/tax-profile.json`.

## Prerequisites

First, read `data/tax-profile.json`. If it doesn't exist or is incomplete, tell the user to run `/tax-start` first.

Required data minimum:
- Filing status
- At least one income source

## Reference Data

Before calculating, read these reference files for accurate rates and rules:
- `references/brackets-2025.md` — tax brackets, standard deduction, qualified dividend rates
- `references/credits-2025.md` — CTC, ACTC, EIC, foreign tax credit, education credits

## Calculation Steps

### Step 1: Total Income (Form 1040 Line 9)
- Line 1: Sum all W2 wages (box 1)
- Line 2b: Interest income (1099-INT)
- Line 3b: Ordinary dividends (1099-DIV box 1a)
- Line 7: Net capital gain/loss from Schedule D (1099-B + 1099-DA)
- Line 8: Other income
- Line 9: Total = sum of above

### Step 2: Adjusted Gross Income (Line 11)
- Line 10: Above-the-line adjustments (HSA, student loan interest, IRA — check domains.* in profile)
- Line 11: AGI = Total Income - Adjustments

### Step 3: Deductions (Line 13)
- Use standard deduction from `references/brackets-2025.md` unless itemized
- If itemized: sum SALT (capped $10,000), mortgage interest, charitable

### Step 4: Taxable Income (Line 15)
- Line 15 = AGI - Deductions
- If negative, taxable income = $0

### Step 5: Tax Calculation (Line 16)
- Apply brackets from `references/brackets-2025.md` based on filing status
- Use Qualified Dividends and Capital Gain Tax Worksheet for qualified dividends and LTCG (taxed at 0%/15%/20% rates)

### Step 6: Credits (Lines 19-21)
- Read rules from `references/credits-2025.md`
- Child Tax Credit: $2,000/child, nonrefundable portion limited to tax
- Other nonrefundable credits as applicable
- Line 22: Tax - nonrefundable credits (minimum $0)

### Step 7: Other Taxes (Line 23)
- Self-employment tax (if Schedule C income exists in domains)
- Additional Medicare tax if applicable

### Step 8: Total Tax (Line 24)
- Line 24 = Line 22 + Line 23

### Step 9: Payments & Refundable Credits (Lines 25-32)
- Line 25: Federal tax withheld (sum all W2 box 2 + 1099 withholding)
- Line 27: EIC (calculate per `references/credits-2025.md`)
- Line 28: Additional Child Tax Credit (refundable ACTC)
- Line 33: Total payments

### Step 10: Refund or Amount Owed
- Line 34: If payments > total tax → REFUND
- Line 37: If total tax > payments → AMOUNT OWED

## Domain Integration

Check for domain-specific data in `tax-profile.json` under `domains.*`:
- `domains.rsu` → invoke `/tax-domain-rsu` reference for basis adjustment rules
- `domains.rental` → compute Schedule E using `/tax-domain-rental` reference
- `domains.harvest` → apply wash sale adjustments per `/tax-domain-harvest` reference
- `domains.crypto` → compute Form 8949 per `/tax-domain-crypto` reference

## Output

Display a clear summary mapping to 1040 line numbers:

```
=== 2025 Federal Tax Return Summary ===

Filing Status: [status]

Line 1  Wages:                    $XX,XXX
Line 2b Interest:                 $X,XXX
Line 3b Ordinary dividends:       $XXX
Line 7  Capital gain/loss:        $X,XXX
Line 9  Total Income:             $XX,XXX
Line 11 AGI:                      $XX,XXX
Line 13 Deduction ([type]):      -$XX,XXX
Line 15 Taxable Income:           $XX,XXX
Line 16 Tax:                      $X,XXX
Line 19 CTC (nonrefundable):     -$X,XXX
Line 24 Total Tax:                $X,XXX

Line 25 Federal Tax Withheld:     $X,XXX
Line 27 EIC:                      $X,XXX
Line 28 ACTC:                     $X,XXX
Line 33 Total Payments:           $X,XXX

>> Line 34 REFUND: $X,XXX  (or Line 37 AMOUNT OWED: $X,XXX)
```

## Save Results

Save the calculation results to `data/tax-calculation.json` with all intermediate values keyed by 1040 line numbers.

Then suggest: "Run `/tax-fill` to generate your completed Form 1040 PDF."
```

- [ ] **Step 4: Commit reference extraction**

```bash
git add skills/tax-calculate/
git commit -m "refactor: extract tax brackets and credits into reference files for tax-calculate"
```

---

### Task 4: Enhance tax-import to Support All 1099 Types

**Files:**
- Modify: `skills/tax-import/SKILL.md`

- [ ] **Step 1: Update tax-import SKILL.md**

Replace the full content of `skills/tax-import/SKILL.md` with:

```markdown
---
name: tax-import
description: Import tax documents like W2 PDFs, 1099s, or brokerage statements. Use when the user wants to import, upload, or parse a tax document.
argument-hint: <file-path>
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion]
---

# Tax Document Import

You are a tax document parser. Extract structured data from tax documents the user provides.

## Usage

The user provides a file path via: `/tax-import <file-path>`

File path from arguments: $ARGUMENTS

## Supported Document Types

### W2 — Wage and Tax Statement
Extract these fields:
- **Box a**: Employee's SSN
- **Box b**: Employer's EIN
- **Box c**: Employer's name and address
- **Box e/f**: Employee's name and address
- **Box 1**: Wages, tips, other compensation
- **Box 2**: Federal income tax withheld
- **Box 3**: Social security wages
- **Box 4**: Social security tax withheld
- **Box 5**: Medicare wages
- **Box 6**: Medicare tax withheld
- **Box 12**: Codes (look for D=401k, DD=health, W=HSA, V=RSU income)
- **Box 14**: Other (RSU, state disability, etc.)
- **Box 15**: State
- **Box 16**: State wages
- **Box 17**: State income tax withheld

**Domain trigger:** If Box 12 code V or Box 14 contains "RSU" or "ESPP", note this in the data and tell the user: "RSU/ESPP income detected. The `/tax-domain-rsu` skill can help ensure correct basis adjustment."

### 1099-B — Proceeds from Broker Transactions
Extract from summary page:
- Short-term: proceeds, cost basis, wash sale loss disallowed, net gain/loss (Form 8949 type A)
- Long-term: proceeds, cost basis, wash sale loss disallowed, net gain/loss (Form 8949 type D)
- Noncovered lots: same fields (Form 8949 type B/E)
- Grand total: proceeds, cost basis, wash sale loss disallowed, net gain/loss
- Federal income tax withheld

**Domain trigger:** If wash sale loss disallowed > 0, note for `/tax-domain-harvest`.

### 1099-DIV — Dividends and Distributions
Extract:
- **Box 1a**: Total ordinary dividends
- **Box 1b**: Qualified dividends
- **Box 2a**: Total capital gain distributions
- **Box 3**: Nondividend distributions
- **Box 4**: Federal income tax withheld
- **Box 5**: Section 199A dividends
- **Box 7**: Foreign tax paid
- **Box 8**: Foreign country

### 1099-INT — Interest Income
Extract:
- **Box 1**: Interest income
- **Box 3**: Interest on US Savings Bonds & Treasury obligations
- **Box 4**: Federal income tax withheld
- **Box 6**: Foreign tax paid

### 1099-DA — Digital Asset Transactions
Extract from summary page:
- Short-term: proceeds, cost basis, net gain/loss (Form 8949 type G/H)
- Long-term: proceeds, cost basis, net gain/loss (Form 8949 type J/K)
- Federal income tax withheld

**Domain trigger:** Always note for `/tax-domain-crypto`.

### 1099-MISC — Miscellaneous Income
Extract:
- **Box 1**: Rents
- **Box 2**: Royalties
- **Box 3**: Other income
- **Box 4**: Federal income tax withheld

**Domain trigger:** If Box 1 (Rents) has a value, note for `/tax-domain-rental`.

## How to Parse

1. Read the file using the Read tool
   - If it's a PDF: Read tool handles PDFs — extract text and look for labeled fields
   - If it's an image (JPG/PNG): Read tool handles images — read the visual content
   - If it's a text/JSON file: parse directly
2. Identify the document type (W2, 1099-B, etc.) from the content
3. Extract all applicable fields listed above
4. Show the extracted data to the user and ask them to confirm or correct
5. Save to `data/tax-profile.json`

## Data Merge

- Read existing `data/tax-profile.json` if it exists (create with default structure if not)
- W2s: Add to `income.w2s[]`. If same employer EIN exists, ask to replace.
- 1099s: Add to `income.otherIncome[]`. If same source+type exists, ask to replace.
- Write back the updated file

## Output

After import, display a clean summary appropriate to the document type:

```
[Document Type] Imported:
  Source: [name] (EIN/TIN: XX-XXXXXXX)
  [Key fields with values]
  Federal Tax Withheld: $X,XXX.XX
```

If domain triggers were detected, mention them.

Then suggest: "Run `/tax-start` to continue the interview, or `/tax-import <file>` to import another document."
```

- [ ] **Step 2: Commit import enhancement**

```bash
git add skills/tax-import/
git commit -m "feat: expand tax-import to support all 1099 types with domain triggers"
```

---

### Task 5: Enhance tax-start with Domain Integration

**Files:**
- Modify: `skills/tax-start/SKILL.md`

- [ ] **Step 1: Update tax-start SKILL.md**

Replace the full content of `skills/tax-start/SKILL.md` with:

```markdown
---
name: tax-start
description: Start the interactive tax filing process. Use when the user wants to begin filing taxes, start a tax return, or says "do my taxes".
argument-hint: [tax-year]
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion]
---

# Tax Filing Interview

You are a tax filing assistant. Guide the user through an interactive interview to collect all information needed to file their federal tax return, similar to TurboTax.

## Tax Year

Default to tax year 2025 (filing in 2026) unless the user specifies otherwise via $ARGUMENTS.

## Interview Flow

Work through these sections **one at a time**. Ask only a few questions per turn. Wait for the user's response before moving to the next section. Be conversational and helpful — explain why you're asking when it's not obvious.

### Section 1: Personal Information
- Full legal name
- Social Security Number (last 4 only for safety — remind user we store locally only)
- Date of birth
- Filing status: Single, Married Filing Jointly, Married Filing Separately, Head of Household, Qualifying Surviving Spouse
- If married: spouse's name and SSN (last 4) or ITIN
- Home address (street, city, state, ZIP)

### Section 2: Dependents
- Do you have any dependents?
- If yes: name, SSN (last 4), relationship, date of birth, months lived with you

### Section 3: Income
- W2 employment income (suggest `/tax-import` if they have the PDF)
- For each W2: employer name, EIN, wages (box 1), federal tax withheld (box 2), state wages, state tax withheld
- **RSU/ESPP:** If user mentions stock compensation, RSU vesting, or ESPP → invoke `/tax-domain-rsu` for specialized questions
- Interest income (1099-INT)
- Dividend income (1099-DIV)
- Capital gains/losses (1099-B) — suggest `/tax-import` for brokerage statements
- **Crypto:** If user mentions cryptocurrency → invoke `/tax-domain-crypto` for specialized questions
- **Rental income:** If user mentions rental property → invoke `/tax-domain-rental` for Schedule E questions
- Any other income (1099-MISC, freelance, etc.)

### Section 4: Deductions
- Ask if they want to itemize or take the standard deduction
- Standard deduction for 2025:
  - Single: $15,000
  - Married Filing Jointly: $30,000
  - Head of Household: $22,500
- If itemizing, collect: state/local taxes (SALT, capped at $10,000), mortgage interest, charitable donations
- Recommend standard deduction unless they clearly benefit from itemizing

### Section 5: Credits
- Any education expenses? (American Opportunity, Lifetime Learning)
- Child tax credit (auto-calculated from dependents)
- Earned Income Credit eligibility
- Any childcare expenses? (Child and Dependent Care Credit)

### Section 6: Other
- Do you want to designate $3 to the Presidential Election Campaign Fund?
- Bank account info for direct deposit refund? (routing + account number)

## Data Storage

After each section, save the collected data to `data/tax-profile.json`. Use this structure:

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
    "rsu": null,
    "rental": null,
    "harvest": null,
    "crypto": null
  },
  "interviewStatus": {
    "completedSections": [],
    "currentSection": "personalInfo",
    "lastUpdated": "2026-04-01"
  }
}
```

## Resume Behavior

Before starting, check if `data/tax-profile.json` exists. If it does:
- Read it and tell the user what you already have
- Offer to resume from where they left off or start over

## Important Notes

- Be reassuring about data privacy — everything stays local on their machine
- If the user seems unsure about something, explain the tax concept briefly
- Don't overwhelm — keep each turn to 2-3 questions max
- After completing all sections, suggest running `/tax-calculate` to compute their return
```

- [ ] **Step 2: Commit interview enhancement**

```bash
git add skills/tax-start/
git commit -m "feat: add domain integration triggers and expanded income types to tax-start"
```

---

### Task 6: Download and Bundle IRS Fillable PDFs

**Files:**
- Create: `forms/` directory
- Download: `forms/f1040-2025.pdf`
- Download: `forms/f1040sb-2025.pdf`
- Download: `forms/f1040sd-2025.pdf`
- Download: `forms/f8949-2025.pdf`

- [ ] **Step 1: Create forms directory**

```bash
mkdir -p forms
```

- [ ] **Step 2: Download IRS fillable PDFs**

Download the official IRS fillable PDF forms for 2025:

```bash
curl -L -o forms/f1040-2025.pdf "https://www.irs.gov/pub/irs-pdf/f1040.pdf"
curl -L -o forms/f1040sb-2025.pdf "https://www.irs.gov/pub/irs-pdf/f1040sb.pdf"
curl -L -o forms/f1040sd-2025.pdf "https://www.irs.gov/pub/irs-pdf/f1040sd.pdf"
curl -L -o forms/f8949-2025.pdf "https://www.irs.gov/pub/irs-pdf/f8949.pdf"
```

Note: IRS URLs may change. If these fail, search `irs.gov` for the current fillable form URLs. The forms should be the fillable/interactive versions, not the print-only versions.

- [ ] **Step 3: Verify PDFs are fillable**

Run a quick check to confirm the PDFs have form fields:

```bash
python3 -c "
from pypdf import PdfReader
r = PdfReader('forms/f1040-2025.pdf')
fields = r.get_fields()
if fields:
    print(f'Found {len(fields)} form fields')
    for i, (name, field) in enumerate(list(fields.items())[:10]):
        print(f'  {name}: {field.get(\"/T\", \"\")}')
else:
    print('ERROR: No form fields found — this may not be the fillable version')
"
```

Expected: `Found XX form fields` with field names listed.

If pypdf is not installed yet, install it first:

```bash
pip3 install pypdf
```

- [ ] **Step 4: Extract all form field names for mapping reference**

```bash
python3 -c "
from pypdf import PdfReader
r = PdfReader('forms/f1040-2025.pdf')
fields = r.get_fields()
if fields:
    for name, field in sorted(fields.items()):
        ft = field.get('/FT', 'unknown')
        print(f'{name} | type={ft}')
" > forms/f1040-field-dump.txt
```

This dump will be used to create the field mapping reference in the next task. Keep this file for reference but don't commit it.

- [ ] **Step 5: Commit forms**

```bash
git add forms/*.pdf
git commit -m "feat: bundle official IRS fillable PDF forms for 2025"
```

---

### Task 7: Create Form 1040 Field Mapping Reference

**Files:**
- Create: `skills/tax-fill/references/form-1040-fields.md`

This task requires reading the field dump from Task 6 and mapping each relevant field to the corresponding `tax-calculation.json` key.

- [ ] **Step 1: Create the tax-fill skill directory**

```bash
mkdir -p skills/tax-fill/references
```

- [ ] **Step 2: Create field mapping reference**

Read `forms/f1040-field-dump.txt` from Task 6 to get exact field names. Then write `skills/tax-fill/references/form-1040-fields.md`.

The field names in IRS PDFs follow a pattern like `topmostSubform[0].Page1[0].f1_XX[0]`. The exact names vary by year, so you MUST read them from the actual PDF. The reference file should look like this (with actual field names from the dump):

```markdown
# Form 1040 PDF Field Mapping (2025)

Maps `data/tax-calculation.json` keys to IRS Form 1040 fillable PDF field names.

## How to Use

The `tax-fill` skill reads this file to know which PDF field to fill with which value.
Format: `PDF Field Name` → `JSON path` → `Description`

## Page 1 — Income

### Filing Status Checkboxes
- `topmostSubform[0].Page1[0].c1_1[0]` → personalInfo.filingStatus == "Single" → Filing status: Single
- `topmostSubform[0].Page1[0].c1_2[0]` → personalInfo.filingStatus == "Married Filing Jointly" → Filing status: MFJ
- `topmostSubform[0].Page1[0].c1_3[0]` → personalInfo.filingStatus == "Married Filing Separately" → Filing status: MFS
- `topmostSubform[0].Page1[0].c1_4[0]` → personalInfo.filingStatus == "Head of Household" → Filing status: HoH
- `topmostSubform[0].Page1[0].c1_5[0]` → personalInfo.filingStatus == "Qualifying Surviving Spouse" → Filing status: QSS

### Name and Address
- `topmostSubform[0].Page1[0].f1_01[0]` → personalInfo.name → Your first name and middle initial
- `topmostSubform[0].Page1[0].f1_02[0]` → personalInfo.name (last) → Last name
- `topmostSubform[0].Page1[0].f1_03[0]` → personalInfo.ssnLast4 → Your SSN
- `topmostSubform[0].Page1[0].f1_04[0]` → personalInfo.spouse.name → Spouse first name
- `topmostSubform[0].Page1[0].f1_05[0]` → personalInfo.spouse.ssnLast4 → Spouse SSN
- `topmostSubform[0].Page1[0].f1_06[0]` → personalInfo.address (full) → Home address

### Income Lines
- `topmostSubform[0].Page1[0].f1_07[0]` → income.wages → Line 1: Wages
- `topmostSubform[0].Page1[0].f1_08[0]` → income.interestIncome → Line 2a: Tax-exempt interest
- `topmostSubform[0].Page1[0].f1_09[0]` → income.interestIncome → Line 2b: Taxable interest
- `topmostSubform[0].Page1[0].f1_10[0]` → income.qualifiedDividends → Line 3a: Qualified dividends
- `topmostSubform[0].Page1[0].f1_11[0]` → income.ordinaryDividends → Line 3b: Ordinary dividends
- `topmostSubform[0].Page1[0].f1_15[0]` → income.capitalGains.netCapitalGains → Line 7: Capital gain/loss
- `topmostSubform[0].Page1[0].f1_17[0]` → totalIncome → Line 9: Total income
- `topmostSubform[0].Page1[0].f1_19[0]` → agi → Line 11: AGI
- `topmostSubform[0].Page1[0].f1_20[0]` → deduction.amount → Line 13: Deductions
- `topmostSubform[0].Page1[0].f1_22[0]` → taxableIncome → Line 15: Taxable income

## Page 2 — Tax and Credits

- `topmostSubform[0].Page2[0].f2_01[0]` → tax.totalTax → Line 16: Tax
- `topmostSubform[0].Page2[0].f2_04[0]` → credits.childTaxCredit.nonrefundable → Line 19: CTC
- `topmostSubform[0].Page2[0].f2_07[0]` → totalTax → Line 24: Total tax
- `topmostSubform[0].Page2[0].f2_08[0]` → payments.federalWithheld → Line 25a: W2 withholding
- `topmostSubform[0].Page2[0].f2_12[0]` → payments.earnedIncomeCredit → Line 27: EIC
- `topmostSubform[0].Page2[0].f2_13[0]` → payments.additionalChildTaxCredit → Line 28: ACTC
- `topmostSubform[0].Page2[0].f2_17[0]` → payments.totalPayments → Line 33: Total payments
- `topmostSubform[0].Page2[0].f2_18[0]` → refundOrOwed.amount → Line 34: Refund / Line 37: Amount owed

**IMPORTANT:** The field names above are EXAMPLES. The actual field names MUST be read from the downloaded PDF using pypdf. Update this file with the real field names after running the field dump in Task 6 Step 4.
```

- [ ] **Step 3: Update field mapping with actual field names from dump**

Read `forms/f1040-field-dump.txt` and update `skills/tax-fill/references/form-1040-fields.md` with the actual field names from the downloaded 2025 Form 1040 PDF. Match each field by its position and label in the PDF to the correct 1040 line number.

- [ ] **Step 4: Commit field mapping**

```bash
git add skills/tax-fill/
git commit -m "feat: create form 1040 field mapping reference for tax-fill"
```

---

### Task 8: Create tax-fill Skill

**Files:**
- Create: `skills/tax-fill/SKILL.md`
- Create: `skills/tax-fill/fill_form.py`

- [ ] **Step 1: Create the fill_form.py helper script**

Write to `skills/tax-fill/fill_form.py`:

```python
#!/usr/bin/env python3
"""Fill IRS Form 1040 PDF with tax calculation data.

Usage:
    python3 fill_form.py <calculation_json> <blank_form_pdf> <output_pdf>

Example:
    python3 fill_form.py data/tax-calculation.json forms/f1040-2025.pdf data/output/1040-2025.pdf
"""

import json
import sys
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("ERROR: pypdf is required. Install with: pip3 install pypdf")
    sys.exit(1)


def load_field_mapping(mapping_path: str) -> dict[str, str]:
    """Parse the field mapping markdown file into a dict of pdf_field -> json_path."""
    mapping = {}
    with open(mapping_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("- `") and "` →" in line:
                parts = line.split("` → ")
                if len(parts) >= 2:
                    pdf_field = parts[0].replace("- `", "")
                    json_path = parts[1].split(" → ")[0].strip("`")
                    mapping[pdf_field] = json_path
    return mapping


def resolve_json_path(data: dict, path: str):
    """Resolve a dotted path like 'income.wages' against a nested dict."""
    keys = path.split(".")
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current


def format_currency(value) -> str:
    """Format a number as currency string for the PDF field."""
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        if value == 0:
            return "0"
        return f"{value:,.2f}"
    return str(value)


def fill_pdf(calculation_path: str, blank_pdf_path: str, output_path: str, mapping_path: str):
    """Fill a blank IRS PDF form with calculated tax data."""
    # Load calculation data
    with open(calculation_path) as f:
        calc_data = json.load(f)

    # Load field mapping
    field_mapping = load_field_mapping(mapping_path)

    if not field_mapping:
        print("ERROR: No field mappings found. Check the mapping file.")
        sys.exit(1)

    # Read blank PDF
    reader = PdfReader(blank_pdf_path)
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)

    # Build field values dict
    field_values = {}
    for pdf_field, json_path in field_mapping.items():
        # Handle filing status checkboxes
        if "filingStatus ==" in json_path:
            status = json_path.split('== "')[1].rstrip('"')
            if calc_data.get("filingStatus") == status:
                field_values[pdf_field] = "/Yes"
            continue

        value = resolve_json_path(calc_data, json_path)
        if value is not None:
            field_values[pdf_field] = format_currency(value)

    # Fill the PDF fields
    filled_count = 0
    for page in writer.pages:
        writer.update_page_form_field_values(page, field_values)

    filled_count = len([v for v in field_values.values() if v])

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Write filled PDF
    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"SUCCESS: Filled {filled_count} fields")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)

    calculation_path = sys.argv[1]
    blank_pdf_path = sys.argv[2]
    output_path = sys.argv[3]

    # Derive mapping path from the script's location
    script_dir = Path(__file__).parent
    mapping_path = script_dir / "references" / "form-1040-fields.md"

    if not Path(calculation_path).exists():
        print(f"ERROR: Calculation file not found: {calculation_path}")
        print("Run /tax-calculate first.")
        sys.exit(1)

    if not Path(blank_pdf_path).exists():
        print(f"ERROR: Blank form not found: {blank_pdf_path}")
        sys.exit(1)

    if not mapping_path.exists():
        print(f"ERROR: Field mapping not found: {mapping_path}")
        sys.exit(1)

    fill_pdf(calculation_path, blank_pdf_path, output_path, str(mapping_path))
```

- [ ] **Step 2: Create tax-fill SKILL.md**

Write to `skills/tax-fill/SKILL.md`:

```markdown
---
name: tax-fill
description: Fill official IRS Form 1040 PDF with calculated tax data and export a mail-ready PDF. Use when the user wants to generate, fill, or export their tax return.
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# Tax Form Filler

Generate a completed, mail-ready IRS Form 1040 PDF from your calculated tax return.

## Prerequisites

- `data/tax-calculation.json` must exist. If not, tell the user to run `/tax-calculate` first.
- Python 3 with `pypdf` must be available. If not: `pip3 install pypdf`
- Blank IRS forms must exist in `forms/` directory.

## Steps

### Step 1: Verify Prerequisites

```bash
python3 -c "from pypdf import PdfReader; print('pypdf OK')"
```

If pypdf is not installed:
```bash
pip3 install pypdf
```

Check that required files exist:
- `data/tax-calculation.json`
- `forms/f1040-2025.pdf`

### Step 2: Fill Form 1040

Run the fill script:

```bash
python3 skills/tax-fill/fill_form.py data/tax-calculation.json forms/f1040-2025.pdf data/output/1040-2025.pdf
```

Expected output: `SUCCESS: Filled XX fields` and `Output: data/output/1040-2025.pdf`

### Step 3: Fill Supporting Schedules (if needed)

Check `data/tax-calculation.json` to determine if additional schedules are required:

- **Schedule B** (required if interest or dividends > $1,500):
  Check if `income.interestIncome > 1500` or `income.ordinaryDividends > 1500`

- **Schedule D** (required if capital gains/losses reported):
  Check if `income.capitalGains` exists with non-zero values

- **Form 8949** (required if Schedule D is needed):
  Needed for individual transaction reporting

For each required schedule, run the fill script with the appropriate form:

```bash
python3 skills/tax-fill/fill_form.py data/tax-calculation.json forms/f1040sd-2025.pdf data/output/schedule-d-2025.pdf
```

Note: Schedule-specific field mappings will need to be added to `references/` as separate files (e.g., `schedule-d-fields.md`). For v1, if a mapping file doesn't exist for a schedule, tell the user which schedule is needed and that they'll need to fill it manually.

### Step 4: Report Results

Tell the user:

```
Form 1040 generated: data/output/1040-2025.pdf
[Schedule D generated: data/output/schedule-d-2025.pdf]
[Form 8949 generated: data/output/form-8949-2025.pdf]

Next steps:
1. Review the PDF to make sure all values are correct
2. Sign and date the return
3. Mail to the IRS (address depends on your state — see instructions)

Optional: Run /tax-compare with a TurboTax return to verify accuracy
```

## Field Mapping

The mapping between calculation JSON keys and PDF form field names is in:
`references/form-1040-fields.md`

Read this file to understand which fields are filled. If a field is missing or wrong, update the mapping file.

## Troubleshooting

- **"No form fields found"**: The PDF may not be the fillable version. Re-download from irs.gov.
- **Fields not filling**: Field names change between tax years. Run the field dump to get current names:
  ```bash
  python3 -c "
  from pypdf import PdfReader
  for name, field in PdfReader('forms/f1040-2025.pdf').get_fields().items():
      print(name)
  "
  ```
  Then update `references/form-1040-fields.md` with the correct field names.
```

- [ ] **Step 3: Create symlink for local development**

```bash
ln -s ../../skills/tax-fill .claude/skills/tax-fill
```

- [ ] **Step 4: Commit tax-fill skill**

```bash
git add skills/tax-fill/ .claude/skills/tax-fill
git commit -m "feat: add tax-fill skill for generating mail-ready IRS Form 1040 PDFs"
```

---

### Task 9: Create forms/ Directory Structure for Future Schedules

**Files:**
- Create: `skills/tax-fill/references/schedule-b-fields.md` (placeholder structure)
- Create: `skills/tax-fill/references/schedule-d-fields.md` (placeholder structure)

- [ ] **Step 1: Create Schedule D field mapping stub**

Write to `skills/tax-fill/references/schedule-d-fields.md`:

```markdown
# Schedule D PDF Field Mapping (2025)

Maps `data/tax-calculation.json` capital gains data to Schedule D fillable PDF field names.

## How to Use

Same as `form-1040-fields.md`. Read actual field names from `forms/f1040sd-2025.pdf`.

## Fields

**IMPORTANT:** Run field dump on the actual PDF to get field names:
```bash
python3 -c "
from pypdf import PdfReader
for name, field in PdfReader('forms/f1040sd-2025.pdf').get_fields().items():
    print(name)
"
```

Then map fields below:

### Part I — Short-Term Capital Gains and Losses
- `[field_name]` → income.capitalGains.shortTerm.proceeds → Line 1a: Short-term from 8949 Box A proceeds
- `[field_name]` → income.capitalGains.shortTerm.costBasis → Line 1a: cost basis
- `[field_name]` → income.capitalGains.shortTerm.washSaleLossDisallowed → Line 1a: adjustments
- `[field_name]` → income.capitalGains.shortTerm.netGainOrLoss → Line 1a: gain/loss
- `[field_name]` → income.capitalGains.shortTermTotal → Line 7: Net short-term

### Part II — Long-Term Capital Gains and Losses
- `[field_name]` → income.capitalGains.longTerm.proceeds → Line 8a: Long-term from 8949 Box D proceeds
- `[field_name]` → income.capitalGains.longTerm.costBasis → Line 8a: cost basis
- `[field_name]` → income.capitalGains.longTerm.netGainOrLoss → Line 8a: gain/loss
- `[field_name]` → income.capitalGains.longTermTotal → Line 15: Net long-term

### Part III — Summary
- `[field_name]` → income.capitalGains.netCapitalGains → Line 16: Combine lines 7 and 15
```

- [ ] **Step 2: Create Schedule B field mapping stub**

Write to `skills/tax-fill/references/schedule-b-fields.md`:

```markdown
# Schedule B PDF Field Mapping (2025)

Maps `data/tax-calculation.json` interest and dividend data to Schedule B fillable PDF field names.

## Fields

**IMPORTANT:** Run field dump on the actual PDF to get field names:
```bash
python3 -c "
from pypdf import PdfReader
for name, field in PdfReader('forms/f1040sb-2025.pdf').get_fields().items():
    print(name)
"
```

### Part I — Interest
- `[field_name]` → (payer name) → Line 1: Payer name
- `[field_name]` → income.interestIncome → Line 1: Amount
- `[field_name]` → income.interestIncome → Line 4: Total interest

### Part II — Ordinary Dividends
- `[field_name]` → (payer name) → Line 5: Payer name
- `[field_name]` → income.ordinaryDividends → Line 5: Amount
- `[field_name]` → income.ordinaryDividends → Line 6: Total dividends
```

- [ ] **Step 3: Commit schedule mapping stubs**

```bash
git add skills/tax-fill/references/
git commit -m "feat: add Schedule B and D field mapping stubs for tax-fill"
```

---

### Task 10: End-to-End Verification

- [ ] **Step 1: Verify plugin structure**

```bash
find /Users/fangyic/ClaudeProjects/taxAgent -type f -not -path '*/\.git/*' -not -path '*/data/*' -not -name '*.pdf' | sort
```

Expected structure:
```
.claude-plugin/plugin.json
.claude/settings.local.json
.claude/skills/tax-calculate -> ../../skills/tax-calculate
.claude/skills/tax-fill -> ../../skills/tax-fill
.claude/skills/tax-import -> ../../skills/tax-import
.claude/skills/tax-start -> ../../skills/tax-start
README.md
docs/superpowers/plans/...
docs/superpowers/specs/...
forms/f1040-2025.pdf
forms/f1040sb-2025.pdf
forms/f1040sd-2025.pdf
forms/f8949-2025.pdf
package.json
skills/tax-calculate/SKILL.md
skills/tax-calculate/references/brackets-2025.md
skills/tax-calculate/references/credits-2025.md
skills/tax-fill/SKILL.md
skills/tax-fill/fill_form.py
skills/tax-fill/references/form-1040-fields.md
skills/tax-fill/references/schedule-b-fields.md
skills/tax-fill/references/schedule-d-fields.md
skills/tax-import/SKILL.md
skills/tax-start/SKILL.md
```

- [ ] **Step 2: Verify all skills are discoverable**

```bash
ls -la .claude/skills/
```

Expected: 4 symlinks pointing to `../../skills/tax-*`

- [ ] **Step 3: Test tax-fill end-to-end**

Using the existing `data/tax-calculation.json` from the current session:

```bash
python3 skills/tax-fill/fill_form.py data/tax-calculation.json forms/f1040-2025.pdf data/output/1040-2025.pdf
```

Expected: `SUCCESS: Filled XX fields` and a PDF at `data/output/1040-2025.pdf`

Open the PDF and verify values are in the correct fields:
- Line 1 should show $10,823.08
- Line 2b should show $977.61
- Line 3b should show $69.69

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "feat: complete plugin restructure with tax-fill — Plan 1 done"
```
