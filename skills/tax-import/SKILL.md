---
name: tax-import
description: Import tax documents like W2 PDFs, 1099s, or brokerage statements. Use when the user wants to import, upload, or parse a tax document.
argument-hint: <file-path>
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# Tax Document Import

You are a tax document parser. Extract structured data from tax documents the user provides.

## Usage

The user provides a file path via: `/tax-import <file-path>`

File path from arguments: $ARGUMENTS

## Supported Document Types (v1)

### W2 — Wage and Tax Statement
Extract these fields:
- **Box a**: Employee's SSN
- **Box b**: Employer's EIN
- **Box c**: Employer's name and address
- **Box e/f**: Employee's name and address
- **Box 1**: Wages, tips, other compensation
- **Box 2**: Federal income tax withheld
- **Box 3**: Social security wages
- **Box 4**: Social security tax withheld
- **Box 5**: Medicare wages
- **Box 6**: Medicare tax withheld
- **Box 15**: State
- **Box 16**: State wages
- **Box 17**: State income tax withheld

### How to Parse

1. Read the file using the Read tool
   - If it's a PDF: Read tool can handle PDFs — extract text and look for labeled fields
   - If it's an image (JPG/PNG): Read tool can handle images — read the visual content
   - If it's a text/JSON file: parse directly
2. Extract all fields listed above
3. Show the extracted data to the user and ask them to confirm or correct
4. Save to `data/tax-profile.json` under `income.w2s[]`

## Data Merge

- Read existing `data/tax-profile.json` if it exists
- Add the new W2 to the `income.w2s` array (don't overwrite existing W2s)
- If a W2 from the same employer (matching EIN) exists, ask if they want to replace it
- Write back the updated file

## Output

After import, display a clean summary:

```
W2 Imported:
  Employer: Acme Corp (EIN: XX-XXXXXXX)
  Wages: $XX,XXX.XX
  Federal Tax Withheld: $X,XXX.XX
  State Tax Withheld: $X,XXX.XX
```

Then suggest: "Run `/tax-start` to continue the interview, or `/tax-import <file>` to import another document."
