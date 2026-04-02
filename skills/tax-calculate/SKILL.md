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
- At least one income source (W2)

## Calculation Steps

### Step 1: Total Income (Line 9 of Form 1040)
- Sum all W2 wages (box 1)
- Add any other income

### Step 2: Adjusted Gross Income (AGI)
- For v1: AGI = Total Income (no above-the-line deductions yet)

### Step 3: Deductions
- If standard deduction selected (or not specified), use 2025 amounts:
  - Single: $15,000
  - Married Filing Jointly: $30,000
  - Married Filing Separately: $15,000
  - Head of Household: $22,500
- If itemized: sum their itemized deductions

### Step 4: Taxable Income
- Taxable Income = AGI - Deductions
- If negative, taxable income = $0

### Step 5: Tax Calculation (2025 Tax Brackets)

**Single:**
| Rate | Bracket |
|------|---------|
| 10% | $0 - $11,925 |
| 12% | $11,926 - $48,475 |
| 22% | $48,476 - $103,350 |
| 24% | $103,351 - $197,300 |
| 32% | $197,301 - $250,525 |
| 35% | $250,526 - $626,350 |
| 37% | Over $626,350 |

**Married Filing Jointly:**
| Rate | Bracket |
|------|---------|
| 10% | $0 - $23,850 |
| 12% | $23,851 - $96,950 |
| 22% | $96,951 - $206,700 |
| 24% | $206,701 - $394,600 |
| 32% | $394,601 - $501,050 |
| 35% | $501,051 - $751,600 |
| 37% | Over $751,600 |

**Head of Household:**
| Rate | Bracket |
|------|---------|
| 10% | $0 - $17,000 |
| 12% | $17,001 - $64,850 |
| 22% | $64,851 - $103,350 |
| 24% | $103,351 - $197,300 |
| 32% | $197,301 - $250,500 |
| 35% | $250,501 - $626,350 |
| 37% | Over $626,350 |

### Step 6: Credits
- Child Tax Credit: $2,000 per qualifying child under 17
- Other credits as applicable

### Step 7: Total Tax
- Tax from brackets - credits = total tax
- Minimum $0

### Step 8: Payments & Refund
- Total federal tax withheld (sum of all W2 box 2)
- If withheld > total tax: REFUND = withheld - total tax
- If withheld < total tax: AMOUNT OWED = total tax - withheld

## Output

Display a clear summary:

```
=== 2025 Federal Tax Return Summary ===

Filing Status: [status]
Total Income: $XX,XXX
Adjusted Gross Income: $XX,XXX
Deduction ([standard/itemized]): -$XX,XXX
Taxable Income: $XX,XXX

Tax: $X,XXX
Credits: -$X,XXX
Total Tax: $X,XXX

Federal Tax Withheld: $X,XXX

>> REFUND: $X,XXX  (or AMOUNT OWED: $X,XXX)
```

## Save Results

Save the calculation results to `data/tax-calculation.json` with all intermediate values for audit trail.

Then suggest: "Run `/tax-fill` to generate your completed Form 1040." (Note: /tax-fill coming in next version)
