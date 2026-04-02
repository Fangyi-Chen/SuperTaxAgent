---
name: tax-domain-rsu
description: RSU and ESPP income tax rules. Invoked by core skills when W2 box 14 contains RSU codes, 1099-B contains ESPP/RSU lots, or user mentions stock compensation during interview.
allowed-tools: [Read, Write, Edit, AskUserQuestion]
---

## Trigger Conditions

Core skills invoke this domain skill when:
- `tax-start`: User mentions RSU vesting, ESPP, stock compensation, equity awards, or "company stock"
- `tax-import`: W2 box 14 contains codes such as RSU, RSUS, ISO, NQ, NQSO, ESPP, or dollar amounts labeled as stock income; or 1099-B lots include "RSU", "ESPP", or "supplemental" in the description field
- `tax-calculate`: `domains.rsu` in tax-profile.json is non-null

## Interview Questions

Ask these questions when triggered. Ask 2-3 at a time; do not overwhelm.

1. "Did you have RSU shares vest in 2025? If so, roughly how many shares, and what was the company's stock price on each vesting date?"
2. "Do you participate in an Employee Stock Purchase Plan (ESPP)? If yes, did you sell any ESPP shares in 2025?"
3. "For any RSU shares you sold in 2025: did you sell them on the same day they vested (same-day sale), use shares to cover taxes (sell-to-cover), or hold them after vesting?"
4. "Check your W2 box 14 — do you see any amounts labeled RSU, ESPP, ISO, NQ, or similar? If yes, what is the label and dollar amount?"
5. "Did your company withhold taxes on RSU vesting using the 22% federal supplemental rate (or 37% if total supplemental income exceeded $1 million)?"
6. "For ESPP: what was the offering date price and the purchase date price? Was the discount 15% or another percentage?"
7. "Have you received a 1099-B for any stock sales? If yes, does it show the cost basis in Box 1e, or is it marked 'cost basis not reported to IRS'?"
8. "Did you exercise any stock options (ISO or NQ/NSO) in 2025?"

## Data Schema

Add under `domains.rsu` in `data/tax-profile.json`:

```json
{
  "domains": {
    "rsu": {
      "hasRSU": true,
      "hasESPP": false,
      "rsuLots": [
        {
          "vestDate": "2025-03-15",
          "sharesVested": 100,
          "fmvAtVest": 42.50,
          "sharesWithheldForTax": 30,
          "saleType": "sell-to-cover",
          "saleDate": "2025-03-15",
          "salePricePerShare": 42.48,
          "w2IncomeReported": 4250.00,
          "federalWithheld": 935.00,
          "supplementalRateUsed": 0.22
        }
      ],
      "esppLots": [
        {
          "offeringDate": "2025-01-01",
          "purchaseDate": "2025-06-30",
          "offeringDateFMV": 38.00,
          "purchaseDateFMV": 44.00,
          "purchasePriceActual": 32.30,
          "sharesPurchased": 50,
          "sharesSold": 50,
          "saleDate": "2025-09-10",
          "salePricePerShare": 46.00,
          "dispositionType": "disqualifying",
          "w2IncomeReported": 580.00
        }
      ],
      "isoExercises": [],
      "nsoExercises": []
    }
  }
}
```

Field notes:
- `saleType`: one of `same-day`, `sell-to-cover`, `hold`, `no-sale`
- `dispositionType` for ESPP: `qualifying` (held >2yr from offering + >1yr from purchase) or `disqualifying`
- `w2IncomeReported`: the dollar amount already included in W2 box 1 for this lot (prevents double-counting)

## Calculation Rules

### RSU Cost Basis
- **Rule:** Cost basis for RSU shares = FMV at vest date × shares received (after withholding).
- **W2 income already included:** The FMV at vest is already in W2 box 1. Do NOT add it again to income.
- **1099-B adjustment:** Brokers often report $0 or incorrect cost basis on 1099-B for RSU. Correct basis = FMV at vest per lot.
- **Form 8949:** Enter corrected basis; use code B (short-term, basis not reported) or E (long-term, basis not reported). Add "Adjusted basis per IRC §1012" in column f.

### RSU Holding Period
- Short-term: sold within 1 year of vest date → Schedule D / Form 8949, Box B or E rates apply
- Long-term: held >1 year from vest date → 0%, 15%, or 20% preferential rates

### ESPP — Qualifying Disposition
Requirements: held >2 years from offering date AND >1 year from purchase date.
- Ordinary income = lesser of: (a) actual gain, or (b) discount at offering date FMV × shares
- Formula: min(sale_price - purchase_price, offering_date_fmv × discount_rate) × shares
- Remaining gain (if any) = long-term capital gain
- Report ordinary income on Schedule 1 line 8 (not in W2 box 1 — employer may not have known)

### ESPP — Disqualifying Disposition
Requirements: sold before meeting qualifying disposition holding periods.
- Ordinary income = (FMV at purchase date - actual purchase price) × shares sold
- This amount MUST appear in W2 box 1 (employer is required to include it)
- Remaining gain/loss = short- or long-term capital gain on Form 8949

### Supplemental Withholding
- Flat 22% federal rate applies to supplemental wages up to $1,000,000
- Above $1,000,000 cumulative supplemental wages in the year: flat 37%
- Supplemental rate withholding often underpays for high earners in high tax brackets — flag underpayment risk

### ISO Exercise
- No regular income tax at exercise (for regular tax purposes)
- AMT preference item = (FMV at exercise - exercise price) × shares (note: AMT calculation out of scope for v1 — flag to user)
- At sale: if qualifying disposition, entire gain is long-term capital gain

### NSO/NQ Exercise
- Ordinary income at exercise = (FMV at exercise - exercise price) × shares exercised
- Must be included in W2 box 1
- Cost basis for future sale = FMV at exercise date

## References

Read `skills/tax-domain-rsu/references/rsu-tax-rules.md` for detailed IRS citations, Publication 525 rules, and Form 8949 instructions.
