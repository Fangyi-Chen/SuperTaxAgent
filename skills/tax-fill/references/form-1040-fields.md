# Form 1040 (2025) PDF Field Mapping Reference

Empirically verified against `forms/f1040-2025.pdf`. All field names use the full
`topmostSubform[0].PageN[0]...` path — **never** the bare leaf name, because the
form contains colliding leaf names (see note on `c1_8` below).

## How this mapping was verified

1. **Text fields**: generate a "probe" PDF that fills every text field with its
   own short name, then read the rendered PDF to see which label appears in
   each box (see `SKILL.md` troubleshooting section for the exact snippet).
2. **Checkboxes**: sort widgets by `/Rect` Y-coordinate (top-to-bottom), then
   correlate with the visible form layout, and read the on-state name from
   each widget's `/AP/N` dictionary (each IRS checkbox has a unique on-state
   like `/1`, `/2`, `/3`, …).

---

## Page 1 — Personal Information

### Name and SSN

| PDF Field                                                  | Description                         | JSON Path                               |
|------------------------------------------------------------|-------------------------------------|-----------------------------------------|
| `topmostSubform[0].Page1[0].f1_14[0]`                      | Your first name and middle initial  | `profile.personalInfo.name` (first+mid) |
| `topmostSubform[0].Page1[0].f1_15[0]`                      | Your last name                      | `profile.personalInfo.name` (last)      |
| `topmostSubform[0].Page1[0].f1_16[0]`                      | Your SSN (max 9 chars, no dashes)   | `profile.personalInfo.ssnLast4`         |
| `topmostSubform[0].Page1[0].f1_17[0]`                      | Spouse first name + middle          | `profile.personalInfo.spouse.name`      |
| `topmostSubform[0].Page1[0].f1_18[0]`                      | Spouse last name                    | `profile.personalInfo.spouse.name`      |
| `topmostSubform[0].Page1[0].f1_19[0]`                      | Spouse SSN (max 9 chars, no dashes) | `profile.personalInfo.spouse.ssnLast4`  |

Note: `f1_01` through `f1_13` are **not** name fields — they are the tax-year-begin
date, combat zone, deceased, and other header-row fields. Do not fill them.

### Address

| PDF Field                                                            | Description                        | JSON Path                                |
|----------------------------------------------------------------------|------------------------------------|------------------------------------------|
| `topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_20[0]`           | Street address                     | `profile.personalInfo.address.street`    |
| `topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_21[0]`           | Apt no.                            | — (not in our data)                      |
| `topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_22[0]`           | City, town, or post office         | `profile.personalInfo.address.city`      |
| `topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_23[0]`           | State                              | `profile.personalInfo.address.state`     |
| `topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_24[0]`           | ZIP code                           | `profile.personalInfo.address.zip`       |
| `topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_25[0]`           | Foreign country                    | — (N/A)                                  |
| `topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_26[0]`           | Foreign province/state             | — (N/A)                                  |
| `topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_27[0]`           | Foreign postal code                | — (N/A)                                  |

### Filing Status Checkboxes — CRITICAL

**Two `c1_8` widgets exist** with different full paths but the same leaf name. Any
approach that addresses fields by leaf alone (including `PyPDFForm`) will fill
**both columns simultaneously**. Use the full qualified path and write `/V` + `/AS`
directly on the widget with the on-state read from `/AP/N`.

| Status                         | Full PDF Path                                                                     | On-state |
|--------------------------------|-----------------------------------------------------------------------------------|----------|
| Single                         | `topmostSubform[0].Page1[0].Checkbox_ReadOrder[0].c1_8[0]`                        | `/1`     |
| Married Filing Jointly         | `topmostSubform[0].Page1[0].Checkbox_ReadOrder[0].c1_8[1]`                        | `/2`     |
| Married Filing Separately      | `topmostSubform[0].Page1[0].Checkbox_ReadOrder[0].c1_8[2]`                        | `/3`     |
| Head of Household              | `topmostSubform[0].Page1[0].c1_8[0]`                                              | `/4`     |
| Qualifying Surviving Spouse    | `topmostSubform[0].Page1[0].c1_8[1]`                                              | `/5`     |

Each checkbox's on-state is unique; `check_checkbox(annot)` in `fill_form.py`
reads `/AP/N` dynamically so you don't need to hard-code these values, but they
are recorded here for reference when debugging.

### Dependents Table

The `Table_Dependents` is organized by **row = attribute, column = dependent**.
For dependent N (1-4):

| Attribute      | PDF Field                                                                              | Field # formula |
|----------------|----------------------------------------------------------------------------------------|-----------------|
| First name     | `topmostSubform[0].Page1[0].Table_Dependents[0].Row1[0].f1_{30+N}[0]`                  | 30+N            |
| Last name      | `topmostSubform[0].Page1[0].Table_Dependents[0].Row2[0].f1_{34+N}[0]`                  | 34+N            |
| SSN            | `topmostSubform[0].Page1[0].Table_Dependents[0].Row3[0].f1_{38+N}[0]`                  | 38+N            |
| Relationship   | `topmostSubform[0].Page1[0].Table_Dependents[0].Row4[0].f1_{42+N}[0]`                  | 42+N            |

CTC/ODC checkboxes live under `Table_Dependents[0].Row5[0].Dependent{N}[0].c1_{10+2N}` etc.
Not currently filled by `fill_form.py`.

---

## Page 1 — Income

| PDF Field                                 | Line | Description                          | JSON Path (nested or flat)                                              |
|-------------------------------------------|------|--------------------------------------|-------------------------------------------------------------------------|
| `topmostSubform[0].Page1[0].f1_47[0]`     | 1a   | Wages from Form W-2 box 1            | `calc.income.wages` / `line1a_wages` / fallback `sum(profile.w2s.box1)` |
| `topmostSubform[0].Page1[0].f1_56[0]`     | 1z   | Total wages (add 1a..1h)             | same as 1a in the common case                                           |
| `topmostSubform[0].Page1[0].f1_58[0]`     | 2b   | Taxable interest                     | `calc.income.interestIncome` / `line2b_interest`                        |
| `topmostSubform[0].Page1[0].f1_59[0]`     | 3a   | Qualified dividends                  | `calc.income.qualifiedDividends` / `line3a_qualifiedDiv`                |
| `topmostSubform[0].Page1[0].f1_60[0]`     | 3b   | Ordinary dividends                   | `calc.income.ordinaryDividends` / `line3b_ordinaryDiv`                  |
| `topmostSubform[0].Page1[0].f1_68[0]`     | 7    | Capital gain or loss (Sch D)         | `calc.income.capitalGains.netCapitalGains` / `line7_capitalGain`        |
| `topmostSubform[0].Page1[0].f1_69[0]`     | 8    | Other income (Sch 1, incl. rental)   | `calc.income.otherIncome` / `line8_otherIncome`                         |
| `topmostSubform[0].Page1[0].f1_70[0]`     | 9    | Total income                         | `calc.income.totalIncome` / `line9_totalIncome`                         |
| `topmostSubform[0].Page1[0].f1_71[0]`     | 10   | Adjustments to income                | `calc.adjustments` / `line10_adjustments`                               |
| `topmostSubform[0].Page1[0].f1_72[0]`     | 11   | AGI                                  | `calc.agi` / `line11_agi`                                               |
| `topmostSubform[0].Page1[0].f1_73[0]`     | 12   | Standard or itemized deduction       | `calc.deduction.amount` / `line12_standardDeduction`                    |
| `topmostSubform[0].Page1[0].f1_75[0]`     | 14   | Add lines 12 + 13                    | same as 12 when no QBI (line 13)                                        |

Sub-lines 1b–1i (`f1_48`–`f1_55`), 2a tax-exempt interest (`f1_57`), IRAs
(`f1_61`/`f1_62`), pensions (`f1_63`/`f1_64`), Social Security (`f1_65`/`f1_66`),
and QBI (`f1_74`) exist on the form but are not populated by `fill_form.py`
unless the corresponding data is present.

---

## Page 2 — Tax, Credits, Payments

| PDF Field                                 | Line | Description                                | JSON Path                                                            |
|-------------------------------------------|------|--------------------------------------------|----------------------------------------------------------------------|
| `topmostSubform[0].Page2[0].f2_01[0]`     | 15   | Taxable income                             | `calc.taxableIncome` / `line15_taxableIncome`                        |
| `topmostSubform[0].Page2[0].f2_02[0]`     | 16   | Tax                                        | `calc.tax.totalTax` / `line16_tax`                                   |
| `topmostSubform[0].Page2[0].f2_04[0]`     | 18   | Add lines 16 + 17                          | same as 16 when no Sch 2 line 3                                      |
| `topmostSubform[0].Page2[0].f2_05[0]`     | 19   | Child tax credit / other dependents credit | `calc.credits.childTaxCredit.nonrefundable` / `line19_ctcNonrefundable` |
| `topmostSubform[0].Page2[0].f2_06[0]`     | 20   | Schedule 3 line 8 (e.g. FTC)               | `calc.credits.schedule3` / `line20_schedule3`                        |
| `topmostSubform[0].Page2[0].f2_07[0]`     | 21   | Line 19 + 20                               | computed                                                             |
| `topmostSubform[0].Page2[0].f2_08[0]`     | 22   | Line 18 minus 21                           | `calc.totalTax` / `line24_totalTax` (before other taxes)             |
| `topmostSubform[0].Page2[0].f2_10[0]`     | 24   | Total tax                                  | `calc.totalTax` / `line24_totalTax`                                  |

### Payments

| PDF Field                                 | Line | Description                        | JSON Path                                                        |
|-------------------------------------------|------|------------------------------------|------------------------------------------------------------------|
| `topmostSubform[0].Page2[0].f2_11[0]`     | 25a  | Federal tax withheld from W-2      | `calc.payments.federalWithheld` / `line25a_w2Withheld`           |
| `topmostSubform[0].Page2[0].f2_12[0]`     | 25b  | Federal tax withheld from 1099s    | `calc.payments.withheld1099` / `line25b_1099Withheld`            |
| `topmostSubform[0].Page2[0].f2_14[0]`     | 25d  | Total withholding (25a+25b+25c)    | computed                                                         |
| `topmostSubform[0].Page2[0].f2_16[0]`     | 27   | Earned income credit (EIC)         | `calc.payments.earnedIncomeCredit` / `line27_eic`                |
| `topmostSubform[0].Page2[0].f2_19[0]`     | 28   | Additional child tax credit        | `calc.payments.additionalChildTaxCredit` / `line28_actc`         |
| `topmostSubform[0].Page2[0].f2_23[0]`     | 32   | Sum of refundable credits          | computed                                                         |
| `topmostSubform[0].Page2[0].f2_24[0]`     | 33   | Total payments                     | `calc.payments.totalPayments` / `line33_totalPayments`           |

### Refund / Amount Owed

| PDF Field                                 | Line | Description       | JSON Path                                                 |
|-------------------------------------------|------|-------------------|-----------------------------------------------------------|
| `topmostSubform[0].Page2[0].f2_25[0]`     | 34   | Overpaid amount   | `calc.refundOrOwed.amount` (if `type == "refund"`)        |
| `topmostSubform[0].Page2[0].f2_26[0]`     | 35a  | Refunded to you   | same as above                                             |
| `topmostSubform[0].Page2[0].f2_29[0]`     | 37   | Amount you owe    | `calc.refundOrOwed.amount` (if `type == "owed"`)          |

---

## Implementation Notes

1. **SSN format**: the SSN fields have `maxLength=9`, so the value must be exactly
   9 characters with no dashes. `fill_form.py` uses a 9-char mask `*****NNNN`; users
   must write in the real digits before mailing.
2. **Name splitting**: `profile.personalInfo.name` is a single string. `split_name()`
   puts everything except the last whitespace-separated token in the first-name
   field, matching how IRS "first name and middle initial" is rendered.
3. **Number formatting**: whole dollars for income/tax lines (`fmt()`), cents for
   withholding/payments/refund (`fmt_cents()`). No `$` or `,` separators.
4. **Checkboxes**: never address by leaf name alone. Always walk `/Parent` to build
   the full qualified path, then read `/AP/N` to discover the widget's on-state.
   See `SKILL.md` §"How fill_form.py works" for the rationale.
5. **Schema tolerance**: when adding new fields, use `pick(obj, "nested.path", "line_numbered_path", default=...)` so the script works with either the
   `tax-calculate` skill's output shape or a hand-written calc JSON.
6. **Year-to-year drift**: IRS renumbers fields each tax year. When updating to a
   new PDF, rerun the probe technique in `SKILL.md` troubleshooting to rediscover
   the text-field mapping, and rerun the `/Rect` Y-sort to relocate checkboxes.
