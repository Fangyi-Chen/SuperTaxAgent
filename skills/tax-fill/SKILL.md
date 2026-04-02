---
name: tax-fill
description: Fill official IRS Form 1040 PDF with calculated tax data and export a mail-ready PDF. Use when the user wants to generate, fill, or export their tax return.
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# Tax Form Filler

Generate a completed, mail-ready IRS Form 1040 PDF from your calculated tax return.

## Prerequisites

- `data/tax-calculation.json` must exist. If not, tell the user to run `/tax-calculate` first.
- `data/tax-profile.json` must exist. If not, tell the user to run `/tax-start` first.
- Python 3 with `pypdf` must be available. If not: `pip3 install pypdf`
- Blank IRS forms must exist in `forms/` directory.

## Steps

### Step 1: Verify Prerequisites

```bash
python3 -c "from pypdf import PdfReader; print('pypdf OK')"
ls data/tax-calculation.json data/tax-profile.json forms/f1040-2025.pdf
```

If pypdf is not installed:
```bash
pip3 install pypdf
```

### Step 2: Fill Form 1040

Run the fill script:

```bash
python3 skills/tax-fill/fill_form.py data/tax-profile.json data/tax-calculation.json forms/f1040-2025.pdf data/output/1040-2025.pdf
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

For v1, if a schedule is needed but its field mapping doesn't exist yet, tell the user which schedule is required and that they'll need to fill it manually.

### Step 4: Report Results

Tell the user:

```
Form 1040 generated: data/output/1040-2025.pdf

IMPORTANT: Review the PDF carefully. Some field mappings are approximate
and may need manual correction. In particular:
- SSN fields show only last 4 digits — you must add your full SSN
- Income sub-line fields (1b-1i) may need verification

Next steps:
1. Open and review the PDF
2. Add full SSN numbers
3. Sign and date the return
4. Mail to the IRS

Optional: Run /tax-compare with a TurboTax return to verify accuracy
```

## Field Mapping

The mapping between data JSON keys and PDF form field names is in:
`references/form-1040-fields.md`

## Troubleshooting

- **"No form fields found"**: The PDF may not be the fillable version. Re-download from irs.gov.
- **Fields not filling**: Field names change between tax years. Dump current field names:
  ```bash
  python3 -c "
  from pypdf import PdfReader
  for name in sorted(PdfReader('forms/f1040-2025.pdf').get_fields().keys()):
      print(name)
  "
  ```
  Then update `references/form-1040-fields.md`.
- **Values in wrong fields**: The field-to-line mapping is approximate. Visually verify and update the mapping reference.
