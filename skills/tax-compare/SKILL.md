---
name: tax-compare
description: Diff two tax return PDFs (ours vs TurboTax or other reference). Extracts field values from both PDFs, compares them line by line against Form 1040 field mapping, and saves a structured diff to data/comparison-{year}.json. Use when the user wants to verify accuracy or contribute improvements.
allowed-tools: [Read, Write, Bash, Glob]
argument-hint: <our-pdf> <reference-pdf>
---

# Tax Return Comparator

Compare this plugin's output against a reference return (e.g., TurboTax) to identify discrepancies.

## Prerequisites

- Python 3 with `pypdf` must be available.
- `data/tax-calculation.json` must exist (provides the expected tax year).
- Both PDF paths must be accessible on the local filesystem.

Check prerequisites:
```bash
python3 -c "from pypdf import PdfReader; print('pypdf OK')"
ls data/tax-calculation.json
```

If pypdf is missing:
```bash
pip3 install pypdf
```

## Arguments

Invocation: `/tax-compare <our-pdf> <reference-pdf>`

- `<our-pdf>` — path to this plugin's generated PDF (e.g., `data/output/1040-2025.pdf`)
- `<reference-pdf>` — path to the TurboTax or other software's PDF

If either argument is missing, ask the user to provide both paths before continuing.

## Steps

### Step 1: Determine Tax Year

Read `data/tax-calculation.json` and extract the `taxYear` field. Use this to name the output file `data/comparison-{year}.json`.

### Step 2: Extract Field Values from Both PDFs

Run the following Python snippet to extract all form field values from each PDF:

```python
from pypdf import PdfReader

def extract_fields(path):
    reader = PdfReader(path)
    fields = reader.get_fields() or {}
    return {
        name: (field.value if hasattr(field, 'value') else str(field))
        for name, field in fields.items()
    }

our_fields = extract_fields("<our-pdf>")
ref_fields = extract_fields("<reference-pdf>")
```

If a PDF has no form fields (e.g., it is a printed/scanned PDF rather than a fillable form), warn the user:
> "The PDF at `<path>` does not contain fillable form fields. Comparison requires a fillable PDF exported directly from TurboTax or this plugin."

### Step 3: Load the 1040 Field Mapping

Read `skills/tax-fill/references/form-1040-fields.md` to get the canonical list of Form 1040 lines and their corresponding PDF field names. This mapping is the authoritative list of fields to compare.

The mapping format is:
```
| Line | Description            | PDF Field Name          | JSON Key                  |
|------|------------------------|-------------------------|---------------------------|
| 1a   | Total wages            | f1_15[0]                | income.totalWages         |
| 11   | AGI                    | f1_32[0]                | adjustedGrossIncome       |
...
```

Build a list of `(line, description, our_field_name, ref_field_name)` tuples to compare. When both PDFs use the same fillable IRS form, field names will match. When the reference PDF uses different field names (e.g., TurboTax-generated), attempt to match by line number from the mapping.

### Step 4: Compare Field by Field

For each mapped field:

1. Extract the numeric value from our PDF and the reference PDF. Strip `$`, `,`, whitespace. Treat empty or missing as `0`.
2. Classify:
   - **match** — values are equal (within $1 rounding tolerance)
   - **mismatch** — values differ
   - **missing_ours** — field present in reference but missing/blank in ours
   - **missing_ref** — field present in ours but missing/blank in reference

Compute `delta = our_value - ref_value` for numeric fields.

### Step 5: Save Comparison to JSON

Write `data/comparison-{year}.json` with the following schema:

```json
{
  "taxYear": 2025,
  "generatedAt": "2026-04-02T00:00:00",
  "ourPdf": "data/output/1040-2025.pdf",
  "referencePdf": "<reference-pdf>",
  "summary": {
    "totalFields": 42,
    "matches": 38,
    "mismatches": 3,
    "missingOurs": 1,
    "missingRef": 0
  },
  "fields": [
    {
      "line": "1a",
      "description": "Total wages",
      "ourValue": 120000,
      "refValue": 120000,
      "delta": 0,
      "status": "match"
    },
    {
      "line": "19",
      "description": "Child tax credit",
      "ourValue": 1648,
      "refValue": 2000,
      "delta": -352,
      "status": "mismatch"
    }
  ]
}
```

### Step 6: Display On-Screen Diff Summary

Print a human-readable summary:

```
Tax Return Comparison — 2025
============================================================
Total fields compared: 42
Matches:    38 ✓
Mismatches:  3 ✗
Missing (ours): 1

MISMATCHES:
  Line 19  Child tax credit       Ours: $1,648   Ref: $2,000   Δ -$352
  Line 25a Estimated tax payments Ours: $0       Ref: $400     Δ -$400
  Line 37  Amount you owe         Ours: $1,200   Ref: $448     Δ +$752

MISSING IN OUR RETURN:
  Line 12b Charitable contribution (no standard ded. limit)

Saved to: data/comparison-2025.json
============================================================
```

### Step 7: Offer Community Contribution

After displaying the diff, ask:

> "Would you like to help improve this tax agent for the community? Your personal tax data stays local — only the line-item deltas and any rule fixes are shared. Run `/tax-evolve` to analyze and propose fixes."

Do not run `/tax-evolve` automatically. Wait for the user to decide.

## Error Handling

- If `data/tax-calculation.json` is missing, tell the user to run `/tax-calculate` first.
- If either PDF path does not exist, show a clear error and stop.
- If pypdf fails to open a PDF (e.g., password-protected), tell the user to export an unlocked copy.
- If no fields are mapped (the field mapping reference is missing), warn and proceed with raw field name matching as a best-effort fallback.
