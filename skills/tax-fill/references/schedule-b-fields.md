# Schedule B PDF Field Mapping (2025)

Maps `data/tax-calculation.json` interest and dividend data to Schedule B fillable PDF field names.

## How to Use

Same pattern as `form-1040-fields.md`. Read actual field names from `forms/f1040sb-2025.pdf`.

## Get Field Names

```bash
python3 -c "
from pypdf import PdfReader
for name in sorted(PdfReader('forms/f1040sb-2025.pdf').get_fields().keys()):
    print(name)
"
```

## Part I — Interest

| PDF Field | Form Line | Description | JSON Path |
|-----------|-----------|-------------|-----------|
| `[field_name]` | Line 1 | Payer name | Source from `profile.income.otherIncome` (1099-INT entries) |
| `[field_name]` | Line 1 | Amount | Per-source interest amount |
| `[field_name]` | Line 4 | Total interest | `calc.income.interestIncome` |

## Part II — Ordinary Dividends

| PDF Field | Form Line | Description | JSON Path |
|-----------|-----------|-------------|-----------|
| `[field_name]` | Line 5 | Payer name | Source from `profile.income.otherIncome` (1099-DIV entries) |
| `[field_name]` | Line 5 | Amount | Per-source dividend amount |
| `[field_name]` | Line 6 | Total ordinary dividends | `calc.income.ordinaryDividends` |
