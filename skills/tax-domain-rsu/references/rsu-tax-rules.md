# RSU and ESPP Tax Rules — IRS Reference

## Governing Law and Publications

- **IRC §83** — Taxation of property transferred in connection with services. FMV at vesting is ordinary income.
- **IRC §421–424** — Statutory stock options (ISO and ESPP).
- **IRS Publication 525** — Taxable and Nontaxable Income (stock options and ESPPs).
- **IRS Publication 550** — Investment Income and Expenses (holding period, capital gains).
- **Form 8949 Instructions** — Reporting sales and dispositions of capital assets.
- **Rev. Rul. 2005-48** — FMV of publicly traded stock determined by average of high and low trading prices on vesting date.

## RSU Taxation at Vesting

### Ordinary Income Recognition (IRC §83(a))
When RSU shares vest, the employee recognizes ordinary income equal to:

  **Income = FMV at vest date × number of shares vested**

- This income is a "wage" and must appear in W2 Box 1 (wages), Box 3 (social security wages), and Box 5 (Medicare wages).
- Box 14 is used by employers to separately disclose the RSU income amount, though this is informational — the amount is already in Box 1.
- Federal income tax withholding applies at the 22% supplemental rate (or 37% above $1M).
- FICA (6.2% SS + 1.45% Medicare) also withheld on vest income.

### Sell-to-Cover Transactions
When shares are withheld to cover taxes:
- Shares withheld are treated as if sold at FMV on vest date.
- The sale typically results in a negligible gain/loss (sale price ≈ FMV used for withholding).
- 1099-B will be issued for withheld shares. Enter on Form 8949 with corrected cost basis = FMV at vest.

### Cost Basis After Vest
  **Basis per share = FMV at vest date**

Broker may report $0 or "N/A" for RSU basis on 1099-B (especially for shares vested before 2014 basis reporting rules). Taxpayer must supply correct basis.

### Holding Period
- Starts the day after vesting date.
- Short-term if sold within 12 months of vest. Long-term if held more than 12 months.

### Form 8949 Coding for RSU Sales
| Situation | Box | Column (f) Adjustment Code |
|-----------|-----|--------------------------|
| Short-term, basis NOT reported to IRS | B | None needed if basis corrected in col (e) |
| Long-term, basis NOT reported to IRS | E | None needed if basis corrected in col (e) |
| Wash sale adjustment | A or D | W |
| Basis was incorrectly reported | A, B, D, or E | B (incorrect basis reported to IRS) |

## ESPP Taxation

### Plan Requirements for Section 423 Treatment (IRC §423)
- Offered to all employees (with limited exclusions).
- Purchase price ≥ 85% of FMV (at offering date or purchase date, whichever is lower).
- Maximum $25,000 FMV of stock purchasable per year.
- Offering period ≤ 27 months.

### Qualifying Disposition
Holding requirements:
1. Shares held more than **2 years** from the offering date, AND
2. Shares held more than **1 year** from the purchase date.

Tax treatment:
- **Ordinary income** = lesser of:
  - (a) Sale price − Purchase price (actual gain), OR
  - (b) Offering date FMV × plan discount rate × shares
- **Capital gain** = any remaining gain beyond ordinary income amount.
- Capital gain is long-term (holding period satisfied by definition).
- Employer is NOT required to include qualifying disposition income in W2 — taxpayer reports on Schedule 1, Line 8.

### Disqualifying Disposition
Any sale that does not meet qualifying disposition holding periods.

Tax treatment:
- **Ordinary income** = (FMV on purchase date − actual purchase price) × shares sold
- **Capital gain/loss** = (Sale price − FMV on purchase date) × shares sold
- Short- or long-term depending on whether held >1 year from purchase date.
- Employer MUST include disqualifying disposition income in W2 Box 1 for the year of sale.

### Double-Count Risk
If employer includes ESPP income in W2 AND taxpayer also enters the full purchase price as basis on 1099-B, the income is counted once. If taxpayer enters $0 basis (as sometimes reported), they must adjust upward to actual purchase price to avoid double-counting the ordinary income portion.

## ISO Taxation (IRC §422)

### At Exercise (Regular Tax)
- No regular income tax recognized at exercise.
- For AMT purposes: preference item = (FMV at exercise − exercise price) × shares (Form 6251 — AMT calculation is out of scope for v1).

### At Sale — Qualifying Disposition
Requirements: held >2 years from grant date AND >1 year from exercise date.
- Entire gain = long-term capital gain.
- **Gain** = sale price − exercise price.
- No ordinary income; no FICA.

### At Sale — Disqualifying Disposition
- **Ordinary income** = lesser of: (FMV at exercise − exercise price) OR (sale price − exercise price).
- Remaining gain (if any) = short- or long-term capital gain.
- Employer reports in W2 Box 1 for year of sale.

## NSO/NQ Taxation (IRC §83)

### At Exercise
- **Ordinary income** = (FMV at exercise − exercise price) × shares.
- Subject to income tax withholding and FICA.
- Must appear in W2 Box 1.

### At Sale
- **Basis** = FMV at exercise date.
- **Gain** = sale price − FMV at exercise.
- Short- or long-term depending on holding period from exercise date.

## Supplemental Wage Withholding Rates (2025)

| Cumulative Supplemental Wages | Federal Withholding Rate |
|-------------------------------|--------------------------|
| Up to $1,000,000 | 22% flat |
| Above $1,000,000 | 37% flat |

Note: Employees in higher marginal brackets (e.g., 32%, 35%, 37%) may be underwithheld at the 22% rate. Flag this risk during calculation.

## Key IRS Forms

- **W2 Box 1:** Total wages including RSU/ESPP/NSO ordinary income.
- **W2 Box 12, Code V:** NSO income included in box 1 (employer may report here).
- **W2 Box 14:** Informational RSU/ESPP amounts (employer discretion; not a second tax).
- **Form 8949:** Report each lot sale (Part I for short-term, Part II for long-term).
- **Schedule D:** Summarize Form 8949 totals; apply capital gains tax rates.
- **Schedule 1, Line 8:** Qualifying ESPP ordinary income (not on W2).
