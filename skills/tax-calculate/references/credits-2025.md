# 2025 Federal Tax Credits Reference

## Child Tax Credit (CTC)

- **Amount:** $2,000 per qualifying child under 17 at end of tax year
- **Nonrefundable:** Limited to tax liability
- **Additional Child Tax Credit (ACTC) — refundable portion:**
  - Maximum refundable: $1,700 per child
  - Formula: 15% x (earned income - $2,500)
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
1. Compute credit = credit_rate x min(earned_income, earned_income_threshold)
2. If AGI > phase-out_begins: reduction = phase-out_rate x (AGI - phase-out_begins)
3. EIC = max(0, credit - reduction)

## Foreign Tax Credit

- Claim as credit (Form 1116) or deduction (Schedule A)
- Nonrefundable — limited to tax liability
- Unused credit can carry back 1 year or forward 10 years
- For amounts <= $300 single / $600 MFJ: can claim directly on 1040 without Form 1116

## Education Credits

### American Opportunity Credit (AOTC)
- Up to $2,500 per eligible student (first 4 years of higher education)
- 100% of first $2,000 + 25% of next $2,000
- 40% refundable (up to $1,000)
- Phase-out: $80,000-$90,000 single / $160,000-$180,000 MFJ

### Lifetime Learning Credit (LLC)
- Up to $2,000 per return (20% of first $10,000 expenses)
- Nonrefundable
- Phase-out: $80,000-$90,000 single / $160,000-$180,000 MFJ
