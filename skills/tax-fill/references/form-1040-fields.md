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

## Page 1 — Income (verified 2025)

Lines 12-14 live on **page 2** in the 2025 form. Page 1 ends at line 11a (AGI).

| PDF Field                                 | Line | Description                          | JSON key (lines shape)  |
|-------------------------------------------|------|--------------------------------------|-------------------------|
| `topmostSubform[0].Page1[0].f1_47[0]`     | 1a   | Total W-2 box 1 wages                | `lines.1a`              |
| `topmostSubform[0].Page1[0].f1_48[0]`     | 1b   | Household employee wages             | `lines.1b`              |
| `topmostSubform[0].Page1[0].f1_49[0]`     | 1c   | Tip income not reported              | `lines.1c`              |
| `topmostSubform[0].Page1[0].f1_50[0]`     | 1d   | Medicaid waiver payments             | `lines.1d`              |
| `topmostSubform[0].Page1[0].f1_51[0]`     | 1e   | Taxable dependent care benefits      | `lines.1e`              |
| `topmostSubform[0].Page1[0].f1_52[0]`     | 1f   | Employer adoption benefits           | `lines.1f`              |
| `topmostSubform[0].Page1[0].f1_53[0]`     | 1g   | Wages from Form 8919                 | `lines.1g`              |
| `topmostSubform[0].Page1[0].f1_55[0]`     | 1h   | Other earned income (amount)         | `lines.1h`              |
| `topmostSubform[0].Page1[0].f1_56[0]`     | 1i   | Nontaxable combat pay election       | `lines.1i`              |
| `topmostSubform[0].Page1[0].f1_57[0]`     | 1z   | Add lines 1a–1h                      | `lines.1z`              |
| `topmostSubform[0].Page1[0].f1_58[0]`     | 2a   | Tax-exempt interest                  | `lines.2a`              |
| `topmostSubform[0].Page1[0].f1_59[0]`     | 2b   | Taxable interest                     | `lines.2b`              |
| `topmostSubform[0].Page1[0].f1_60[0]`     | 3a   | Qualified dividends                  | `lines.3a`              |
| `topmostSubform[0].Page1[0].f1_61[0]`     | 3b   | Ordinary dividends                   | `lines.3b`              |
| `topmostSubform[0].Page1[0].f1_62[0]`     | 4a   | IRA distributions                    | `lines.4a`              |
| `topmostSubform[0].Page1[0].f1_63[0]`     | 4b   | IRAs taxable amount                  | `lines.4b`              |
| `topmostSubform[0].Page1[0].f1_65[0]`     | 5a   | Pensions and annuities               | `lines.5a`              |
| `topmostSubform[0].Page1[0].f1_66[0]`     | 5b   | Pensions taxable amount              | `lines.5b`              |
| `topmostSubform[0].Page1[0].f1_68[0]`     | 6a   | Social Security benefits             | `lines.6a`              |
| `topmostSubform[0].Page1[0].f1_69[0]`     | 6b   | SS taxable amount                    | `lines.6b`              |
| `topmostSubform[0].Page1[0].f1_70[0]`     | 7    | Capital gain or loss (Sch D)         | `lines.7`               |
| `topmostSubform[0].Page1[0].f1_72[0]`     | 8    | Additional income (Sch 1 line 10)    | `lines.8`               |
| `topmostSubform[0].Page1[0].f1_73[0]`     | 9    | Total income                         | `lines.9`               |
| `topmostSubform[0].Page1[0].f1_74[0]`     | 10   | Adjustments (Sch 1 line 26)          | `lines.10`              |
| `topmostSubform[0].Page1[0].f1_75[0]`     | 11a  | Adjusted gross income (AGI)          | `lines.11a` / `lines.11`|

---

## Page 2 — Tax, Credits, Payments (verified 2025)

| PDF Field                                 | Line | Description                                | JSON key                 |
|-------------------------------------------|------|--------------------------------------------|--------------------------|
| `topmostSubform[0].Page2[0].f2_01[0]`     | 11b  | AGI (restated from 11a)                    | `lines.11b` / `lines.11` |
| `topmostSubform[0].Page2[0].f2_02[0]`     | 12e  | Standard or itemized deduction             | `lines.12e` / `lines.12` |
| `topmostSubform[0].Page2[0].f2_03[0]`     | 13a  | QBI (Form 8995/8995-A)                     | `lines.13a`              |
| `topmostSubform[0].Page2[0].f2_04[0]`     | 13b  | Additional deductions (Sch 1-A)            | `lines.13b`              |
| `topmostSubform[0].Page2[0].f2_05[0]`     | 14   | Add lines 12e + 13a + 13b                  | `lines.14`               |
| `topmostSubform[0].Page2[0].f2_06[0]`     | 15   | Taxable income                             | `lines.15`               |
| `topmostSubform[0].Page2[0].f2_08[0]`     | 16   | Tax                                        | `lines.16`               |
| `topmostSubform[0].Page2[0].f2_09[0]`     | 17   | Sch 2 line 3                               | `lines.17`               |
| `topmostSubform[0].Page2[0].f2_10[0]`     | 18   | Add 16 + 17                                | `lines.18`               |
| `topmostSubform[0].Page2[0].f2_11[0]`     | 19   | Child tax credit / ODC                     | `lines.19`               |
| `topmostSubform[0].Page2[0].f2_12[0]`     | 20   | Sch 3 line 8                               | `lines.20`               |
| `topmostSubform[0].Page2[0].f2_13[0]`     | 21   | Line 19 + 20                               | `lines.21`               |
| `topmostSubform[0].Page2[0].f2_14[0]`     | 22   | Line 18 − line 21                          | `lines.22`               |
| `topmostSubform[0].Page2[0].f2_15[0]`     | 23   | Other taxes (Sch 2 line 21)                | `lines.23`               |
| `topmostSubform[0].Page2[0].f2_16[0]`     | 24   | Total tax                                  | `lines.24`               |

### Payments

| PDF Field                                 | Line | Description                        | JSON key      |
|-------------------------------------------|------|------------------------------------|---------------|
| `topmostSubform[0].Page2[0].f2_17[0]`     | 25a  | Federal tax withheld from W-2      | `lines.25a`   |
| `topmostSubform[0].Page2[0].f2_18[0]`     | 25b  | Federal tax withheld from 1099s    | `lines.25b`   |
| `topmostSubform[0].Page2[0].f2_19[0]`     | 25c  | Other withholding                  | `lines.25c`   |
| `topmostSubform[0].Page2[0].f2_20[0]`     | 25d  | Total withholding (25a+25b+25c)    | `lines.25d`   |
| `topmostSubform[0].Page2[0].f2_23[0]`     | 27   | Earned income credit (EIC)         | `lines.27`    |
| `topmostSubform[0].Page2[0].f2_24[0]`     | 28   | Additional child tax credit (ACTC) | `lines.28`    |
| `topmostSubform[0].Page2[0].f2_29[0]`     | 33   | Total payments                     | `lines.33`    |

### Refund / Amount Owed

| PDF Field                                 | Line | Description        | JSON key                      |
|-------------------------------------------|------|--------------------|-------------------------------|
| `topmostSubform[0].Page2[0].f2_30[0]`     | 34   | Overpaid amount    | `lines.34` (refund)           |
| `topmostSubform[0].Page2[0].f2_31[0]`     | 35a  | Refunded to you    | `lines.35a` / `lines.34`      |
| `topmostSubform[0].Page2[0].f2_32[0]`     | 35b  | Routing number     | `profile.other.directDeposit` |
| `topmostSubform[0].Page2[0].f2_33[0]`     | 35d  | Account number     | `profile.other.directDeposit` |
| `topmostSubform[0].Page2[0].f2_35[0]`     | 37   | Amount you owe     | `lines.37`                    |

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
