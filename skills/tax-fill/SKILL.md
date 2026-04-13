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

```bash
python3 skills/tax-fill/fill_form.py data/tax-profile.json data/tax-calculation.json forms/f1040-2025.pdf data/output/1040-2025.pdf
```

Expected output:
```
SUCCESS: Filled 43 text fields, 1 checkboxes
Output: data/output/1040-2025.pdf
```

The exact counts vary by filing status and data, but the script reports both text fields and checkboxes separately. If "0 checkboxes" appears, filing status did not get set and the PDF will render with a blank Filing Status area.

### Step 3: Fill Supporting Schedules (if needed)

Check `data/tax-calculation.json` to determine if additional schedules are required:

- **Schedule B** (required if interest or dividends > $1,500)
- **Schedule D** (required if capital gains/losses reported)
- **Form 8949** (required if Schedule D is needed)
- **Schedule E** (required if rental income reported under `domains.rental`)
- **Schedule 1** (required if other income exists beyond W-2/1099-INT/DIV/B)

For v1, if a schedule is needed but its field mapping doesn't exist yet, tell the user which schedule is required and that they will need to fill it manually.

### Step 4: Report Results

Tell the user:

```
Form 1040 generated: data/output/1040-2025.pdf

IMPORTANT: Review the PDF carefully.
- SSN fields show a 9-character mask like *****NNNN — you must add your full SSN before mailing
- Review income line amounts against your source documents
- Attach supporting schedules (Schedule B / D / E / Form 8949) as applicable

Next steps:
1. Open and review the PDF
2. Add full SSN numbers
3. Sign and date the return
4. Mail to the IRS

Optional: Run /tax-compare with a TurboTax return to verify accuracy
```

## How `fill_form.py` Works

Critical design decisions — read before modifying:

### 1. Two-pass fill: text fields vs checkboxes
Text fields are set via pypdf's `update_page_form_field_values()`. Checkboxes are set by **walking the page annotation tree directly**, matching each target checkbox by its *fully qualified* field path (e.g. `topmostSubform[0].Page1[0].Checkbox_ReadOrder[0].c1_8[1]`), then writing both `/V` and `/AS` on the widget.

### 2. Checkboxes use unique on-states
Each IRS checkbox widget has its own appearance-state name — `/1`, `/2`, `/3`, `/4`, `/5` — read from the widget's `/AP/N` dictionary. Do not hard-code `/Yes` or `"1"`. The `check_checkbox(annot)` helper reads `/AP/N` and picks the first non-`/Off` key.

### 3. Full qualified paths disambiguate colliding leaf names
Form 1040 has *two* widgets both named `c1_8[0]` — one under `Checkbox_ReadOrder` (Single filing status), one at the page level (Head of Household). Any library that addresses fields by leaf name alone (including `PyPDFForm`) will fill **both** simultaneously. Always match by the full subform path.

### 4. Schema tolerance via `pick()`
`fill_form.py` uses `pick(obj, *paths, default)` to try multiple key paths into `tax-calculation.json`. It accepts both nested shapes (`calc.income.wages`, `calc.payments.federalWithheld`) and flat line-numbered shapes (`line1a_wages`, `line25a_w2Withheld`). When in doubt it falls back to deriving raw figures from the profile (`profile.income.w2s[]` for wages, `profile.income.otherIncome[]` for 1099 totals).

### 5. Filing status source of truth
Filing status is personal info, not a computation. The script reads `profile.personalInfo.filingStatus` first, falling back to `calc.filingStatus`. It also normalizes camelCase (`MarriedFilingJointly`) and spaced forms (`Married Filing Jointly`) to a canonical Title Case key.

## Field Mapping

The empirically-verified mapping between PDF field paths and Form 1040 lines is in:
`references/form-1040-fields.md`

## Troubleshooting

- **"No form fields found"**: The PDF may not be the fillable version. Re-download from irs.gov.
- **Filing status box appears blank even though script reports 1 checkbox filled**: Verify both `/V` and `/AS` were written:
  ```bash
  python3 -c "
  from pypdf import PdfReader
  r = PdfReader('data/output/1040-2025.pdf')
  for p in r.pages:
      for a in p.get('/Annots', []):
          o = a.get_object()
          if o.get('/FT') == '/Btn' and o.get('/V') is not None and str(o.get('/V')) != '/Off':
              print(o.get('/V'), o.get('/AS'))
  "
  ```
  Both values should match and neither should be `/Off`.
- **Values appear in the wrong text fields**: Field numbers shift year to year. Use the probe technique to visually verify:
  ```bash
  python3 -c "
  from pypdf import PdfReader, PdfWriter
  r = PdfReader('forms/f1040-2025.pdf')
  w = PdfWriter()
  w.clone_document_from_reader(r)
  vals = {}
  for name, f in r.get_fields().items():
      if str(f.get('/FT','')) == '/Tx' and 'Page1' in name:
          vals[name] = name.split('.')[-1].replace('[0]','')
  for page in w.pages:
      w.update_page_form_field_values(page, vals)
  with open('data/output/_field_probe.pdf','wb') as fh:
      w.write(fh)
  "
  ```
  Every text field is labeled with its own short name — read off the correct mapping visually and update `references/form-1040-fields.md`.
- **Checkbox locations unknown**: Use `/Rect` Y-coordinates to order widgets top-to-bottom on the page:
  ```bash
  python3 -c "
  from pypdf import PdfReader
  r = PdfReader('forms/f1040-2025.pdf')
  for a in r.pages[0]['/Annots']:
      o = a.get_object()
      if o.get('/FT') != '/Btn': continue
      parts = []; c = o
      while c is not None:
          t = c.get('/T')
          if t: parts.append(str(t))
          c = c.get('/Parent')
      nm = '.'.join(reversed(parts))
      rect = o.get('/Rect')
      print(f\"y={float(rect[1]):6.1f}  x={float(rect[0]):6.1f}  {nm}\")
  " | sort -r
  ```
- **Fields still empty after fill**: Check that `fill_form.py` didn't silently filter out a zero or `None` value. Empty string values are dropped; `"0"` is kept.
