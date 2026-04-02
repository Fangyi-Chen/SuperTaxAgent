# Form 1040 (2024) PDF Field Mapping Reference

Maps `data/tax-profile.json` and `data/tax-calculation.json` keys to actual PDF field names in `forms/f1040-2025.pdf`.

## Notation

- **PDF Field**: Full `topmostSubform[0].PageN[0]...` path used by the PDF form filler
- **JSON Path**: Dot-notation path into our data files (`profile.` = tax-profile.json, `calc.` = tax-calculation.json)
- **(verify)**: Mapping is approximate; confirm against the actual PDF before relying on it

---

## Page 1 — Personal Information

### Your Name and SSN

| PDF Field | Form Line | Description | JSON Path |
|-----------|-----------|-------------|-----------|
| `topmostSubform[0].Page1[0].f1_01[0]` | Top | Your first name and middle initial | `profile.personalInfo.name` (first + middle) |
| `topmostSubform[0].Page1[0].f1_02[0]` | Top | Your last name | `profile.personalInfo.name` (last) |
| `topmostSubform[0].Page1[0].f1_03[0]` | Top | Your SSN | `profile.personalInfo.ssnLast4` (full SSN needed) |
| `topmostSubform[0].Page1[0].f1_04[0]` | Top | Spouse first name and middle initial | `profile.personalInfo.spouse.name` (first + middle) |
| `topmostSubform[0].Page1[0].f1_05[0]` | Top | Spouse last name | `profile.personalInfo.spouse.name` (last) |
| `topmostSubform[0].Page1[0].f1_06[0]` | Top | Spouse SSN | `profile.personalInfo.spouse.ssnLast4` (full SSN needed) |

### Address

| PDF Field | Form Line | Description | JSON Path |
|-----------|-----------|-------------|-----------|
| `topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_20[0]` | Address | Street address | `profile.personalInfo.address.street` |
| `topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_21[0]` | Address | Apt no. | — (not in our data) |
| `topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_22[0]` | Address | City, town or post office | `profile.personalInfo.address.city` |
| `topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_23[0]` | Address | State | `profile.personalInfo.address.state` |
| `topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_24[0]` | Address | ZIP code | `profile.personalInfo.address.zip` |
| `topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_25[0]` | Address | Foreign country name | — (not applicable) |
| `topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_26[0]` | Address | Foreign province/state | — (not applicable) |
| `topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_27[0]` | Address | Foreign postal code | — (not applicable) |

### Filing Status Checkboxes

| PDF Field | Form Line | Description | JSON Path / Condition |
|-----------|-----------|-------------|----------------------|
| `topmostSubform[0].Page1[0].c1_1[0]` | Filing Status | Single | `calc.filingStatus == "Single"` |
| `topmostSubform[0].Page1[0].c1_2[0]` | Filing Status | Married filing jointly | `calc.filingStatus == "Married Filing Jointly"` |
| `topmostSubform[0].Page1[0].c1_3[0]` | Filing Status | Married filing separately | `calc.filingStatus == "Married Filing Separately"` |
| `topmostSubform[0].Page1[0].c1_4[0]` | Filing Status | Head of household | `calc.filingStatus == "Head of Household"` |
| `topmostSubform[0].Page1[0].c1_5[0]` | Filing Status | Qualifying surviving spouse | `calc.filingStatus == "Qualifying Surviving Spouse"` |

### Other Header Fields (verify)

| PDF Field | Form Line | Description | JSON Path |
|-----------|-----------|-------------|-----------|
| `topmostSubform[0].Page1[0].f1_07[0]` | MFS spouse | Spouse name if MFS (verify) | — |
| `topmostSubform[0].Page1[0].f1_08[0]` | Digital assets | Digital assets question (verify) | `profile.income.otherIncome` (has 1099-DA → "Yes") |
| `topmostSubform[0].Page1[0].c1_6[0]` | Digital assets | Digital assets "Yes" checkbox (verify) | Check if 1099-DA exists |
| `topmostSubform[0].Page1[0].c1_7[0]` | Digital assets | Digital assets "No" checkbox (verify) | Check if no 1099-DA |
| `topmostSubform[0].Page1[0].c1_8[0]` | Std deduction | You as dependent checkbox (verify) | — |

### Dependents Table

| PDF Field | Form Line | Description | JSON Path |
|-----------|-----------|-------------|-----------|
| `topmostSubform[0].Page1[0].Table_Dependents[0].Row1[0].f1_31[0]` | Dependents | Dependent 1 name | `profile.dependents[0].name` |
| `topmostSubform[0].Page1[0].Table_Dependents[0].Row1[0].f1_32[0]` | Dependents | Dependent 1 SSN | `profile.dependents[0].ssnLast4` (full SSN needed) |
| `topmostSubform[0].Page1[0].Table_Dependents[0].Row1[0].f1_33[0]` | Dependents | Dependent 1 relationship | `profile.dependents[0].relationship` |
| `topmostSubform[0].Page1[0].Table_Dependents[0].Row1[0].f1_34[0]` | Dependents | Dependent 1 CTC checkbox | `calc.credits.childTaxCredit.qualifyingChildren >= 1` |

---

## Page 1 — Income Section

Field numbers f1_47 through f1_75 map to income lines. The exact mapping depends on the 2024 form revision. Below is the best-effort mapping based on standard line ordering.

| PDF Field | Form Line | Description | JSON Path |
|-----------|-----------|-------------|-----------|
| `topmostSubform[0].Page1[0].f1_47[0]` | Line 1a | Wages, salaries, tips | `calc.income.wages` |
| `topmostSubform[0].Page1[0].f1_48[0]` | Line 1b | Household employee income (verify) | — |
| `topmostSubform[0].Page1[0].f1_49[0]` | Line 1c | Tip income not on W-2 (verify) | — |
| `topmostSubform[0].Page1[0].f1_50[0]` | Line 1d | Medicaid waiver payments (verify) | — |
| `topmostSubform[0].Page1[0].f1_51[0]` | Line 1e | Dependent care benefits (verify) | — |
| `topmostSubform[0].Page1[0].f1_52[0]` | Line 1f | Employer-provided adoption benefits (verify) | — |
| `topmostSubform[0].Page1[0].f1_53[0]` | Line 1g | Form 8919 wages (verify) | — |
| `topmostSubform[0].Page1[0].f1_54[0]` | Line 1h | Strike benefits (verify) | — |
| `topmostSubform[0].Page1[0].f1_55[0]` | Line 1i | Stock option income (verify) | — |
| `topmostSubform[0].Page1[0].f1_56[0]` | Line 1z | Add 1a through 1i (verify) | `calc.income.wages` (same if only W-2 wages) |
| `topmostSubform[0].Page1[0].f1_57[0]` | Line 2a | Tax-exempt interest | — (not in our data) |
| `topmostSubform[0].Page1[0].f1_58[0]` | Line 2b | Taxable interest | `calc.income.interestIncome` |
| `topmostSubform[0].Page1[0].f1_59[0]` | Line 3a | Qualified dividends | `calc.income.qualifiedDividends` |
| `topmostSubform[0].Page1[0].f1_60[0]` | Line 3b | Ordinary dividends | `calc.income.ordinaryDividends` |
| `topmostSubform[0].Page1[0].f1_61[0]` | Line 4a | IRA distributions | — |
| `topmostSubform[0].Page1[0].f1_62[0]` | Line 4b | IRA distributions taxable | — |
| `topmostSubform[0].Page1[0].f1_63[0]` | Line 5a | Pensions and annuities | — |
| `topmostSubform[0].Page1[0].f1_64[0]` | Line 5b | Pensions taxable amount | — |
| `topmostSubform[0].Page1[0].f1_65[0]` | Line 6a | Social security benefits | — |
| `topmostSubform[0].Page1[0].f1_66[0]` | Line 6b | Social security taxable | — |
| `topmostSubform[0].Page1[0].f1_67[0]` | Line 6c | Election to exclude lump-sum (verify) | — |
| `topmostSubform[0].Page1[0].f1_68[0]` | Line 7 | Capital gain or loss | `calc.income.capitalGains.netCapitalGains` |
| `topmostSubform[0].Page1[0].f1_69[0]` | Line 8 | Other income (Sched 1) | — |
| `topmostSubform[0].Page1[0].f1_70[0]` | Line 9 | Total income | `calc.income.totalIncome` |
| `topmostSubform[0].Page1[0].f1_71[0]` | Line 10 | Adjustments to income | `calc.adjustments` |
| `topmostSubform[0].Page1[0].f1_72[0]` | Line 11 | Adjusted gross income (AGI) | `calc.agi` |
| `topmostSubform[0].Page1[0].f1_73[0]` | Line 12 | Standard/itemized deduction | `calc.deduction.amount` |
| `topmostSubform[0].Page1[0].f1_74[0]` | Line 13 | Qualified business income deduction | — |
| `topmostSubform[0].Page1[0].f1_75[0]` | Line 14 | Total deductions (12 + 13) | `calc.deduction.amount` (same, no QBI) |

> **Note**: Lines 1b-1i fields (f1_48 through f1_55) are sub-lines of wages. Our data only has total W-2 wages, so we fill Line 1a and Line 1z. The field numbering between f1_56 and f1_68 may shift by 1-2 positions depending on the exact PDF layout. Fields marked (verify) should be confirmed by inspecting the PDF.

---

## Page 2 — Tax, Credits, Payments

| PDF Field | Form Line | Description | JSON Path |
|-----------|-----------|-------------|-----------|
| `topmostSubform[0].Page2[0].f2_01[0]` | Line 15 | Taxable income | `calc.taxableIncome` |
| `topmostSubform[0].Page2[0].f2_02[0]` | Line 16 | Tax | `calc.tax.totalTax` |
| `topmostSubform[0].Page2[0].f2_03[0]` | Line 17 | Amount from Schedule 2, Part I, line 4 (verify) | — |
| `topmostSubform[0].Page2[0].f2_04[0]` | Line 18 | Sum of lines 16 and 17 | `calc.tax.totalTax` (no Sched 2 amount) |
| `topmostSubform[0].Page2[0].f2_05[0]` | Line 19 | Child tax credit / other credits | `calc.credits.childTaxCredit.nonrefundable` |
| `topmostSubform[0].Page2[0].f2_06[0]` | Line 20 | Amount from Schedule 3, Part I, line 8 (verify) | — |
| `topmostSubform[0].Page2[0].f2_07[0]` | Line 21 | Sum of lines 19 and 20 | `calc.credits.childTaxCredit.nonrefundable` |
| `topmostSubform[0].Page2[0].f2_08[0]` | Line 22 | Line 18 minus line 21 | `calc.tax.totalTax` (0 in our case) |
| `topmostSubform[0].Page2[0].f2_09[0]` | Line 23 | Other taxes from Schedule 2 (verify) | — |
| `topmostSubform[0].Page2[0].f2_10[0]` | Line 24 | Total tax | `calc.totalTax` |

### Payments Section

| PDF Field | Form Line | Description | JSON Path |
|-----------|-----------|-------------|-----------|
| `topmostSubform[0].Page2[0].f2_11[0]` | Line 25a | Federal tax withheld (W-2s) | `calc.payments.federalWithheld` |
| `topmostSubform[0].Page2[0].f2_12[0]` | Line 25b | Federal tax withheld (1099s) | — (0 in our data) |
| `topmostSubform[0].Page2[0].f2_13[0]` | Line 25c | Other withholding forms | — |
| `topmostSubform[0].Page2[0].f2_14[0]` | Line 25d | Total withholding (sum) | `calc.payments.federalWithheld` |
| `topmostSubform[0].Page2[0].f2_15[0]` | Line 26 | Estimated tax payments | — |
| `topmostSubform[0].Page2[0].f2_16[0]` | Line 27a | Earned income credit (EIC) | `calc.payments.earnedIncomeCredit` |
| `topmostSubform[0].Page2[0].f2_17[0]` | Line 27b | Nontaxable combat pay (verify) | — |
| `topmostSubform[0].Page2[0].f2_18[0]` | Line 27c | Prior year EIC amount (verify) | — |
| `topmostSubform[0].Page2[0].f2_19[0]` | Line 28 | Additional child tax credit (Sched 8812) | `calc.payments.additionalChildTaxCredit` |
| `topmostSubform[0].Page2[0].f2_20[0]` | Line 29 | American opportunity credit | — |
| `topmostSubform[0].Page2[0].f2_21[0]` | Line 30 | Reserved for future use (verify) | — |
| `topmostSubform[0].Page2[0].f2_22[0]` | Line 31 | Amount from Schedule 3, Part II | — |
| `topmostSubform[0].Page2[0].f2_23[0]` | Line 32 | Sum of 27a+28+29+30+31 | `calc.payments.earnedIncomeCredit + calc.payments.additionalChildTaxCredit` |
| `topmostSubform[0].Page2[0].f2_24[0]` | Line 33 | Total payments | `calc.payments.totalPayments` |

### Refund Section

| PDF Field | Form Line | Description | JSON Path |
|-----------|-----------|-------------|-----------|
| `topmostSubform[0].Page2[0].f2_25[0]` | Line 34 | Overpaid amount | `calc.refundOrOwed.amount` (if type == "refund") |
| `topmostSubform[0].Page2[0].f2_26[0]` | Line 35a | Refunded to you | `calc.refundOrOwed.amount` (if type == "refund") |
| `topmostSubform[0].Page2[0].RoutingNo[0].f2_32[0]` | Line 35b | Routing number | `profile.other.directDeposit` (not yet configured) |
| `topmostSubform[0].Page2[0].AccountNo[0].f2_33[0]` | Line 35d | Account number | `profile.other.directDeposit` (not yet configured) |
| `topmostSubform[0].Page2[0].f2_27[0]` | Line 35b | Account type checkbox area (verify) | — |

### Amount Owed / Penalty

| PDF Field | Form Line | Description | JSON Path |
|-----------|-----------|-------------|-----------|
| `topmostSubform[0].Page2[0].f2_28[0]` | Line 36 | Applied to next year's estimated tax (verify) | — |
| `topmostSubform[0].Page2[0].f2_29[0]` | Line 37 | Amount you owe | `calc.refundOrOwed.amount` (if type == "owed") |
| `topmostSubform[0].Page2[0].f2_30[0]` | Line 38 | Estimated tax penalty (verify) | — |

---

## Page 2 — Checkboxes

| PDF Field | Form Line | Description | JSON Path / Condition |
|-----------|-----------|-------------|----------------------|
| `topmostSubform[0].Page2[0].c2_1[0]` | Line 16 | Tax checkbox (Form 8814, etc.) (verify) | — |
| `topmostSubform[0].Page2[0].c2_7[0]` | Line 27 | EIC checkbox — nontaxable pay (verify) | — |
| `topmostSubform[0].Page2[0].c2_8[0]` | Line 35b | Checking account type (verify) | — |
| `topmostSubform[0].Page2[0].c2_9[0]` | Line 35b | Savings account type (verify) | — |

---

## Fields We Fill for Our Return

Summary of fields actually populated from our data (Fangyi Chen, MFJ, TY 2025):

| Form Line | Value | PDF Field |
|-----------|-------|-----------|
| First name | Fangyi | `Page1[0].f1_01[0]` |
| Last name | Chen | `Page1[0].f1_02[0]` |
| SSN | ***-**-0921 | `Page1[0].f1_03[0]` |
| Spouse first name | Qiqi | `Page1[0].f1_04[0]` |
| Spouse last name | Hao | `Page1[0].f1_05[0]` |
| Spouse SSN | ***-**-4528 | `Page1[0].f1_06[0]` |
| Street | 2628 139th Ave SE | `Address_ReadOrder[0].f1_20[0]` |
| City | Bellevue | `Address_ReadOrder[0].f1_22[0]` |
| State | WA | `Address_ReadOrder[0].f1_23[0]` |
| ZIP | 98005 | `Address_ReadOrder[0].f1_24[0]` |
| Filing status | MFJ | `Page1[0].c1_2[0]` |
| Digital assets | Yes | `Page1[0].c1_6[0]` (verify) |
| Dependent 1 name | Chloe Hao Chen | `Table_Dependents[0].Row1[0].f1_31[0]` |
| Dependent 1 SSN | ***-**-7703 | `Table_Dependents[0].Row1[0].f1_32[0]` |
| Dependent 1 relation | daughter | `Table_Dependents[0].Row1[0].f1_33[0]` |
| Dependent 1 CTC | Yes | `Table_Dependents[0].Row1[0].f1_34[0]` |
| Line 1a (wages) | 10,823.08 | `Page1[0].f1_47[0]` |
| Line 1z (total wages) | 10,823.08 | `Page1[0].f1_56[0]` (verify) |
| Line 2b (taxable interest) | 977.61 | `Page1[0].f1_58[0]` (verify) |
| Line 3a (qualified div) | 68.53 | `Page1[0].f1_59[0]` (verify) |
| Line 3b (ordinary div) | 69.69 | `Page1[0].f1_60[0]` (verify) |
| Line 7 (capital gains) | 929.01 | `Page1[0].f1_68[0]` (verify) |
| Line 9 (total income) | 12,799.39 | `Page1[0].f1_70[0]` (verify) |
| Line 10 (adjustments) | 0 | `Page1[0].f1_71[0]` (verify) |
| Line 11 (AGI) | 12,799.39 | `Page1[0].f1_72[0]` (verify) |
| Line 12 (std deduction) | 30,000 | `Page1[0].f1_73[0]` (verify) |
| Line 14 (total deductions) | 30,000 | `Page1[0].f1_75[0]` (verify) |
| Line 15 (taxable income) | 0 | `Page2[0].f2_01[0]` |
| Line 16 (tax) | 0 | `Page2[0].f2_02[0]` |
| Line 24 (total tax) | 0 | `Page2[0].f2_10[0]` (verify) |
| Line 25a (W-2 withheld) | 482.68 | `Page2[0].f2_11[0]` (verify) |
| Line 25d (total withheld) | 482.68 | `Page2[0].f2_14[0]` (verify) |
| Line 27a (EIC) | 3,679.85 | `Page2[0].f2_16[0]` (verify) |
| Line 28 (add'l CTC) | 1,248.46 | `Page2[0].f2_19[0]` (verify) |
| Line 33 (total payments) | 5,410.99 | `Page2[0].f2_24[0]` (verify) |
| Line 34 (overpaid) | 5,410.99 | `Page2[0].f2_25[0]` (verify) |
| Line 35a (refunded) | 5,410.99 | `Page2[0].f2_26[0]` (verify) |

---

## Implementation Notes

1. **SSN fields**: Our data only stores last-4 digits. Full SSNs must be provided at fill time (never stored in repo).
2. **Name splitting**: `tax-profile.json` stores full names. The fill script must split into first/last for the PDF fields.
3. **Checkbox values**: IRS PDF checkboxes typically use value `1` or `Yes` for checked state. Test with the actual PDF.
4. **Number formatting**: The IRS form expects numbers without `$` signs. Round to nearest dollar for most lines, or show cents where the form allows.
5. **Field verification**: All fields marked (verify) should be confirmed by running `pdftk forms/f1040-2025.pdf dump_data_fields` and cross-referencing the field order with a visual inspection of the PDF.
6. **Page 2 field offsets**: The f2_XX numbering may not be perfectly sequential with form lines. The offset between field numbers and line numbers can vary. Verify with actual PDF inspection.
