# Schedule D PDF Field Mapping (2025)

Maps `data/tax-calculation.json` capital gains data to Schedule D fillable PDF field names.

## How to Use

Same pattern as `form-1040-fields.md`. Read actual field names from `forms/f1040sd-2025.pdf`.

## Get Field Names

```bash
python3 -c "
from pypdf import PdfReader
for name in sorted(PdfReader('forms/f1040sd-2025.pdf').get_fields().keys()):
    print(name)
"
```

## Part I — Short-Term Capital Gains and Losses

| PDF Field | Form Line | Description | JSON Path |
|-----------|-----------|-------------|-----------|
| `[field_name]` | Line 1a | Short-term from 8949 Box A — proceeds | `calc.income.capitalGains.shortTerm.proceeds` |
| `[field_name]` | Line 1a | cost basis | `calc.income.capitalGains.shortTerm.costBasis` |
| `[field_name]` | Line 1a | adjustments (wash sale) | `calc.income.capitalGains.shortTerm.washSaleLossDisallowed` |
| `[field_name]` | Line 1a | gain/loss | `calc.income.capitalGains.shortTerm.netGainOrLoss` |
| `[field_name]` | Line 7 | Net short-term capital gain/loss | `calc.income.capitalGains.shortTermTotal` |

## Part II — Long-Term Capital Gains and Losses

| PDF Field | Form Line | Description | JSON Path |
|-----------|-----------|-------------|-----------|
| `[field_name]` | Line 8a | Long-term from 8949 Box D — proceeds | `calc.income.capitalGains.longTerm.proceeds` |
| `[field_name]` | Line 8a | cost basis | `calc.income.capitalGains.longTerm.costBasis` |
| `[field_name]` | Line 8a | gain/loss | `calc.income.capitalGains.longTerm.netGainOrLoss` |
| `[field_name]` | Line 15 | Net long-term capital gain/loss | `calc.income.capitalGains.longTermTotal` |

## Part III — Summary

| PDF Field | Form Line | Description | JSON Path |
|-----------|-----------|-------------|-----------|
| `[field_name]` | Line 16 | Combine lines 7 and 15 | `calc.income.capitalGains.netCapitalGains` |
