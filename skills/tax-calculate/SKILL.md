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
