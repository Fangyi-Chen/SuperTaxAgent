#!/usr/bin/env python3
"""Fill IRS Form 1040 PDF with tax calculation data.

Usage:
    python3 fill_form.py <profile_json> <calculation_json> <blank_form_pdf> <output_pdf>

Example:
    python3 fill_form.py data/tax-profile.json data/tax-calculation.json forms/f1040-2025.pdf data/output/1040-2025.pdf
"""

import json
import sys
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("ERROR: pypdf is required. Install with: pip3 install pypdf")
    sys.exit(1)


def split_name(full_name: str) -> tuple[str, str]:
    """Split a full name into (first+middle, last)."""
    parts = full_name.strip().split()
    if len(parts) <= 1:
        return (full_name, "")
    return (" ".join(parts[:-1]), parts[-1])


def fmt(value) -> str:
    """Format a number for the PDF field. No dollar signs, round to nearest dollar."""
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        if value == 0:
            return "0"
        # Round to whole dollars for most fields
        return str(round(value))
    return str(value)


def fmt_cents(value) -> str:
    """Format with cents for withholding/payment fields."""
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        if value == 0:
            return "0"
        return f"{value:.2f}"
    return str(value)


def build_field_values(profile: dict, calc: dict) -> dict[str, str]:
    """Build a mapping of PDF field names to values from profile and calculation data."""
    fields = {}
    pi = profile.get("personalInfo", {})
    addr = pi.get("address", {})
    spouse = pi.get("spouse", {})
    deps = profile.get("dependents", [])
    income = calc.get("income", {})
    cap = income.get("capitalGains", {})
    payments = calc.get("payments", {})
    refund = calc.get("refundOrOwed", {})

    # --- Page 1: Personal Info ---
    first, last = split_name(pi.get("name", ""))
    fields["topmostSubform[0].Page1[0].f1_01[0]"] = first
    fields["topmostSubform[0].Page1[0].f1_02[0]"] = last
    # SSN - only last 4, user must add full SSN manually
    fields["topmostSubform[0].Page1[0].f1_03[0]"] = f"***-**-{pi.get('ssnLast4', '')}"

    if spouse:
        sp_first, sp_last = split_name(spouse.get("name", ""))
        fields["topmostSubform[0].Page1[0].f1_04[0]"] = sp_first
        fields["topmostSubform[0].Page1[0].f1_05[0]"] = sp_last
        fields["topmostSubform[0].Page1[0].f1_06[0]"] = f"***-**-{spouse.get('ssnLast4', '')}"

    # Address
    fields["topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_20[0]"] = addr.get("street", "")
    fields["topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_22[0]"] = addr.get("city", "")
    fields["topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_23[0]"] = addr.get("state", "")
    fields["topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_24[0]"] = addr.get("zip", "")

    # Filing status checkbox
    status = calc.get("filingStatus", pi.get("filingStatus", ""))
    status_map = {
        "Single": "topmostSubform[0].Page1[0].c1_1[0]",
        "Married Filing Jointly": "topmostSubform[0].Page1[0].c1_2[0]",
        "Married Filing Separately": "topmostSubform[0].Page1[0].c1_3[0]",
        "Head of Household": "topmostSubform[0].Page1[0].c1_4[0]",
        "Qualifying Surviving Spouse": "topmostSubform[0].Page1[0].c1_5[0]",
    }
    if status in status_map:
        fields[status_map[status]] = "1"

    # Dependents (up to 4)
    dep_rows = [
        ("Row1", "f1_31", "f1_32", "f1_33", "f1_34"),
        ("Row2", "f1_35", "f1_36", "f1_37", "f1_38"),
        ("Row3", "f1_39", "f1_40", "f1_41", "f1_42"),
        ("Row4", "f1_43", "f1_44", "f1_45", "f1_46"),
    ]
    for i, dep in enumerate(deps[:4]):
        row, fn, fs, fr, fc = dep_rows[i]
        base = f"topmostSubform[0].Page1[0].Table_Dependents[0].{row}[0]"
        fields[f"{base}.{fn}[0]"] = dep.get("name", "")
        fields[f"{base}.{fs}[0]"] = f"***-**-{dep.get('ssnLast4', '')}"
        fields[f"{base}.{fr}[0]"] = dep.get("relationship", "")

    # --- Page 1: Income ---
    fields["topmostSubform[0].Page1[0].f1_47[0]"] = fmt(income.get("wages"))
    fields["topmostSubform[0].Page1[0].f1_56[0]"] = fmt(income.get("wages"))  # Line 1z
    fields["topmostSubform[0].Page1[0].f1_58[0]"] = fmt(income.get("interestIncome"))  # Line 2b
    fields["topmostSubform[0].Page1[0].f1_59[0]"] = fmt(income.get("qualifiedDividends"))  # Line 3a
    fields["topmostSubform[0].Page1[0].f1_60[0]"] = fmt(income.get("ordinaryDividends"))  # Line 3b
    fields["topmostSubform[0].Page1[0].f1_68[0]"] = fmt(cap.get("netCapitalGains"))  # Line 7
    fields["topmostSubform[0].Page1[0].f1_70[0]"] = fmt(income.get("totalIncome"))  # Line 9
    fields["topmostSubform[0].Page1[0].f1_71[0]"] = fmt(calc.get("adjustments", 0))  # Line 10
    fields["topmostSubform[0].Page1[0].f1_72[0]"] = fmt(calc.get("agi"))  # Line 11
    fields["topmostSubform[0].Page1[0].f1_73[0]"] = fmt(calc.get("deduction", {}).get("amount"))  # Line 12
    fields["topmostSubform[0].Page1[0].f1_75[0]"] = fmt(calc.get("deduction", {}).get("amount"))  # Line 14

    # --- Page 2: Tax ---
    fields["topmostSubform[0].Page2[0].f2_01[0]"] = fmt(calc.get("taxableIncome"))  # Line 15
    fields["topmostSubform[0].Page2[0].f2_02[0]"] = fmt(calc.get("tax", {}).get("totalTax"))  # Line 16
    fields["topmostSubform[0].Page2[0].f2_04[0]"] = fmt(calc.get("tax", {}).get("totalTax"))  # Line 18
    ctc_nr = calc.get("credits", {}).get("childTaxCredit", {}).get("nonrefundable", 0)
    fields["topmostSubform[0].Page2[0].f2_05[0]"] = fmt(ctc_nr)  # Line 19
    fields["topmostSubform[0].Page2[0].f2_07[0]"] = fmt(ctc_nr)  # Line 21
    fields["topmostSubform[0].Page2[0].f2_08[0]"] = fmt(calc.get("totalTax"))  # Line 22
    fields["topmostSubform[0].Page2[0].f2_10[0]"] = fmt(calc.get("totalTax"))  # Line 24

    # --- Page 2: Payments ---
    fields["topmostSubform[0].Page2[0].f2_11[0]"] = fmt_cents(payments.get("federalWithheld"))  # Line 25a
    fields["topmostSubform[0].Page2[0].f2_14[0]"] = fmt_cents(payments.get("federalWithheld"))  # Line 25d
    fields["topmostSubform[0].Page2[0].f2_16[0]"] = fmt_cents(payments.get("earnedIncomeCredit"))  # Line 27a
    fields["topmostSubform[0].Page2[0].f2_19[0]"] = fmt_cents(payments.get("additionalChildTaxCredit"))  # Line 28
    # Line 32: sum of refundable credits
    refundable_sum = (payments.get("earnedIncomeCredit", 0) or 0) + (payments.get("additionalChildTaxCredit", 0) or 0)
    fields["topmostSubform[0].Page2[0].f2_23[0]"] = fmt_cents(refundable_sum)
    fields["topmostSubform[0].Page2[0].f2_24[0]"] = fmt_cents(payments.get("totalPayments"))  # Line 33

    # --- Page 2: Refund ---
    if refund.get("type") == "refund":
        fields["topmostSubform[0].Page2[0].f2_25[0]"] = fmt_cents(refund.get("amount"))  # Line 34
        fields["topmostSubform[0].Page2[0].f2_26[0]"] = fmt_cents(refund.get("amount"))  # Line 35a
    elif refund.get("type") == "owed":
        fields["topmostSubform[0].Page2[0].f2_29[0]"] = fmt_cents(refund.get("amount"))  # Line 37

    # Remove empty values
    return {k: v for k, v in fields.items() if v and v != "0" and v != "***-**-"}


def fill_pdf(profile_path: str, calc_path: str, blank_pdf_path: str, output_path: str):
    """Fill a blank IRS PDF form with tax data."""
    with open(profile_path) as f:
        profile = json.load(f)
    with open(calc_path) as f:
        calc = json.load(f)

    field_values = build_field_values(profile, calc)

    reader = PdfReader(blank_pdf_path)
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)

    # Fill fields on all pages
    for page in writer.pages:
        writer.update_page_form_field_values(page, field_values)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        writer.write(f)

    filled = len(field_values)
    print(f"SUCCESS: Filled {filled} fields")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(1)

    profile_path, calc_path, blank_path, output_path = sys.argv[1:5]

    for path, label in [(profile_path, "Profile"), (calc_path, "Calculation"), (blank_path, "Blank form")]:
        if not Path(path).exists():
            print(f"ERROR: {label} file not found: {path}")
            sys.exit(1)

    fill_pdf(profile_path, calc_path, blank_path, output_path)
