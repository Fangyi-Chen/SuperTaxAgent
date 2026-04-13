#!/usr/bin/env python3
"""Fill IRS Form 1040 PDF with tax calculation data.

Usage:
    python3 fill_form.py <profile_json> <calculation_json> <blank_form_pdf> <output_pdf>

Design notes:
  - Text fields are filled via pypdf's update_page_form_field_values().
  - Checkboxes are filled by walking the annotation tree, matching each target
    by its *fully qualified* field path (to disambiguate colliding leaf names
    like two `c1_8[0]` widgets), then setting /V and /AS to the widget's
    actual appearance-state name (read from /AP/N). Each IRS checkbox has its
    own unique on-state (/1, /2, /3, ...), not a shared "/Yes".
  - Schema-tolerant: accepts both nested (calc.income.wages) and flat
    line-numbered (line1a_wages) shapes for the calculation JSON.
"""

import json
import re
import sys
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import NameObject, DictionaryObject, ArrayObject
except ImportError:
    print("ERROR: pypdf is required. Install with: pip3 install pypdf")
    sys.exit(1)


# ------------------------- helpers -------------------------

def split_name(full_name: str) -> tuple[str, str]:
    parts = (full_name or "").strip().split()
    if len(parts) <= 1:
        return (full_name or "", "")
    return (" ".join(parts[:-1]), parts[-1])


def fmt(value) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, (int, float)):
        return str(round(value))
    return str(value)


def fmt_cents(value) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, (int, float)):
        return f"{value:.2f}"
    return str(value)


def pick(obj, *paths, default=None):
    for path in paths:
        cur = obj
        ok = True
        for key in path.split("."):
            if isinstance(cur, dict) and key in cur:
                cur = cur[key]
            else:
                ok = False
                break
        if ok and cur is not None:
            return cur
    return default


def normalize_filing_status(s: str) -> str:
    if not s:
        return ""
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", s)
    return " ".join(s.split()).title()


def sum_w2(profile: dict, field: str) -> float:
    total = 0.0
    for w2 in profile.get("income", {}).get("w2s", []) or []:
        v = w2.get(field)
        if isinstance(v, (int, float)):
            total += v
    return total


def sum_1099_interest(profile: dict) -> float:
    total = 0.0
    for item in profile.get("income", {}).get("otherIncome", []) or []:
        if item.get("type") == "1099-INT":
            v = item.get("box1_interest") or item.get("interest") or 0
            if isinstance(v, (int, float)):
                total += v
    return total


def sum_1099_div(profile: dict, key_ord: bool = True) -> float:
    total = 0.0
    for item in profile.get("income", {}).get("otherIncome", []) or []:
        if item.get("type") == "1099-DIV":
            if key_ord:
                v = item.get("box1a_ordinaryDiv") or item.get("ordinaryDividends") or 0
            else:
                v = item.get("box1b_qualifiedDiv") or item.get("qualifiedDividends") or 0
            if isinstance(v, (int, float)):
                total += v
    return total


def sum_1099_withheld(profile: dict) -> float:
    total = 0.0
    for item in profile.get("income", {}).get("otherIncome", []) or []:
        v = item.get("box4_fedWithheld") or item.get("fedWithheld") or 0
        if isinstance(v, (int, float)):
            total += v
    return total


# ------------------------- field building -------------------------

def build_text_fields(profile: dict, calc: dict) -> tuple[dict, set]:
    """Return (text_field_map, checkbox_paths_to_check)."""
    fields: dict[str, str] = {}
    checkboxes: set[str] = set()

    pi = profile.get("personalInfo", {}) or {}
    taxpayer = pi.get("taxpayer", {}) if isinstance(pi.get("taxpayer"), dict) else {}
    name = pi.get("name") or taxpayer.get("name") or ""
    ssn_last4 = pi.get("ssnLast4") or taxpayer.get("ssnLast4") or ""
    spouse = pi.get("spouse", {}) or {}
    addr = pi.get("address", {}) or {}
    deps = profile.get("dependents", []) or []

    # Personal info (f1_14..f1_19 verified empirically)
    first, last = split_name(name)
    fields["topmostSubform[0].Page1[0].f1_14[0]"] = first
    fields["topmostSubform[0].Page1[0].f1_15[0]"] = last
    if ssn_last4:
        fields["topmostSubform[0].Page1[0].f1_16[0]"] = f"*****{ssn_last4}"
    if spouse:
        sp_first, sp_last = split_name(spouse.get("name", ""))
        fields["topmostSubform[0].Page1[0].f1_17[0]"] = sp_first
        fields["topmostSubform[0].Page1[0].f1_18[0]"] = sp_last
        if spouse.get("ssnLast4"):
            fields["topmostSubform[0].Page1[0].f1_19[0]"] = f"*****{spouse['ssnLast4']}"

    fields["topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_20[0]"] = addr.get("street", "")
    fields["topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_22[0]"] = addr.get("city", "")
    fields["topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_23[0]"] = addr.get("state", "")
    fields["topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_24[0]"] = addr.get("zip", "")

    # Filing status — verified empirically by annotation /Rect positions and
    # widget /AP/N states. Each checkbox has a unique on-state.
    status_raw = pi.get("filingStatus") or calc.get("filingStatus", "")
    status = normalize_filing_status(status_raw)
    status_checkbox_map = {
        "Single":                      "topmostSubform[0].Page1[0].Checkbox_ReadOrder[0].c1_8[0]",
        "Married Filing Jointly":      "topmostSubform[0].Page1[0].Checkbox_ReadOrder[0].c1_8[1]",
        "Married Filing Separately":   "topmostSubform[0].Page1[0].Checkbox_ReadOrder[0].c1_8[2]",
        "Head Of Household":           "topmostSubform[0].Page1[0].c1_8[0]",
        "Qualifying Surviving Spouse": "topmostSubform[0].Page1[0].c1_8[1]",
    }
    if status in status_checkbox_map:
        checkboxes.add(status_checkbox_map[status])

    # Dependents
    tbl = "topmostSubform[0].Page1[0].Table_Dependents[0]"
    for i, dep in enumerate(deps[:4]):
        col = i + 1
        first_nm, last_nm = split_name(dep.get("name", ""))
        fields[f"{tbl}.Row1[0].f1_{30+col}[0]"] = first_nm
        fields[f"{tbl}.Row2[0].f1_{34+col}[0]"] = last_nm
        if dep.get("ssnLast4"):
            fields[f"{tbl}.Row3[0].f1_{38+col}[0]"] = f"*****{dep['ssnLast4']}"
        fields[f"{tbl}.Row4[0].f1_{42+col}[0]"] = dep.get("relationship", "")

    # --- Derive figures ---
    wages = sum_w2(profile, "box1_wages")
    fed_w2 = sum_w2(profile, "box2_fedWithheld")
    fed_1099 = sum_1099_withheld(profile)
    interest = sum_1099_interest(profile)
    ord_div = sum_1099_div(profile, True)
    qual_div = sum_1099_div(profile, False)

    c_wages = pick(calc, "income.wages", "line1a_wages", default=wages)
    c_interest = pick(calc, "income.interestIncome", "line2b_interest", default=interest)
    c_qdiv = pick(calc, "income.qualifiedDividends", "line3a_qualifiedDiv", default=qual_div)
    c_odiv = pick(calc, "income.ordinaryDividends", "line3b_ordinaryDiv", default=ord_div)
    c_capgain = pick(calc, "income.capitalGains.netCapitalGains", "line7_capitalGain")
    c_other = pick(calc, "income.otherIncome", "line8_otherIncome", default=0)
    c_total_income = pick(calc, "income.totalIncome", "line9_totalIncome")
    c_adj = pick(calc, "adjustments", "line10_adjustments", default=0)
    c_agi = pick(calc, "agi", "line11_agi")
    c_ded = pick(calc, "deduction.amount", "line12_standardDeduction")
    c_taxable = pick(calc, "taxableIncome", "line15_taxableIncome")
    c_tax16 = pick(calc, "tax.totalTax", "line16_tax")
    c_ctc_nr = pick(calc, "credits.childTaxCredit.nonrefundable", "line19_ctcNonrefundable", default=0)
    c_sch3 = pick(calc, "credits.schedule3", "line20_schedule3", default=0)
    c_total_tax = pick(calc, "totalTax", "line24_totalTax")
    c_w2_wh = pick(calc, "payments.federalWithheld", "line25a_w2Withheld", default=fed_w2)
    c_1099_wh = pick(calc, "payments.withheld1099", "line25b_1099Withheld", default=fed_1099)
    c_eic = pick(calc, "payments.earnedIncomeCredit", "line27_eic", default=0)
    c_actc = pick(calc, "payments.additionalChildTaxCredit", "line28_actc", default=0)
    c_total_pay = pick(calc, "payments.totalPayments", "line33_totalPayments")
    c_refund = pick(calc, "refundOrOwed.amount", "line34_refund")
    c_refund_type = pick(calc, "refundOrOwed.type")
    c_owed = pick(calc, "line37_amountOwed", default=0)
    if c_refund_type is None:
        if c_refund and c_refund > 0:
            c_refund_type = "refund"
        elif c_owed and c_owed > 0:
            c_refund_type = "owed"

    # Page 1 income
    fields["topmostSubform[0].Page1[0].f1_47[0]"] = fmt(c_wages)
    fields["topmostSubform[0].Page1[0].f1_56[0]"] = fmt(c_wages)
    fields["topmostSubform[0].Page1[0].f1_58[0]"] = fmt(c_interest)
    fields["topmostSubform[0].Page1[0].f1_59[0]"] = fmt(c_qdiv)
    fields["topmostSubform[0].Page1[0].f1_60[0]"] = fmt(c_odiv)
    fields["topmostSubform[0].Page1[0].f1_68[0]"] = fmt(c_capgain)
    fields["topmostSubform[0].Page1[0].f1_69[0]"] = fmt(c_other)
    fields["topmostSubform[0].Page1[0].f1_70[0]"] = fmt(c_total_income)
    fields["topmostSubform[0].Page1[0].f1_71[0]"] = fmt(c_adj)
    fields["topmostSubform[0].Page1[0].f1_72[0]"] = fmt(c_agi)
    fields["topmostSubform[0].Page1[0].f1_73[0]"] = fmt(c_ded)
    fields["topmostSubform[0].Page1[0].f1_75[0]"] = fmt(c_ded)

    # Page 2
    fields["topmostSubform[0].Page2[0].f2_01[0]"] = fmt(c_taxable)
    fields["topmostSubform[0].Page2[0].f2_02[0]"] = fmt(c_tax16)
    fields["topmostSubform[0].Page2[0].f2_04[0]"] = fmt(c_tax16)
    fields["topmostSubform[0].Page2[0].f2_05[0]"] = fmt(c_ctc_nr)
    fields["topmostSubform[0].Page2[0].f2_06[0]"] = fmt(c_sch3)
    fields["topmostSubform[0].Page2[0].f2_07[0]"] = fmt((c_ctc_nr or 0) + (c_sch3 or 0))
    fields["topmostSubform[0].Page2[0].f2_08[0]"] = fmt(c_total_tax)
    fields["topmostSubform[0].Page2[0].f2_10[0]"] = fmt(c_total_tax)
    fields["topmostSubform[0].Page2[0].f2_11[0]"] = fmt_cents(c_w2_wh)
    fields["topmostSubform[0].Page2[0].f2_12[0]"] = fmt_cents(c_1099_wh)
    fields["topmostSubform[0].Page2[0].f2_14[0]"] = fmt_cents((c_w2_wh or 0) + (c_1099_wh or 0))
    fields["topmostSubform[0].Page2[0].f2_16[0]"] = fmt_cents(c_eic)
    fields["topmostSubform[0].Page2[0].f2_19[0]"] = fmt_cents(c_actc)
    fields["topmostSubform[0].Page2[0].f2_23[0]"] = fmt_cents((c_eic or 0) + (c_actc or 0))
    fields["topmostSubform[0].Page2[0].f2_24[0]"] = fmt_cents(c_total_pay)

    if c_refund_type == "refund":
        fields["topmostSubform[0].Page2[0].f2_25[0]"] = fmt_cents(c_refund)
        fields["topmostSubform[0].Page2[0].f2_26[0]"] = fmt_cents(c_refund)
    elif c_refund_type == "owed":
        fields["topmostSubform[0].Page2[0].f2_29[0]"] = fmt_cents(c_owed)

    # Strip truly empty values
    fields = {k: v for k, v in fields.items() if v != "" and v is not None}
    return fields, checkboxes


# ------------------------- writing -------------------------

def annotation_fullname(annot) -> str:
    """Walk /Parent chain to build a fully qualified field name."""
    parts = []
    cur = annot
    while cur is not None:
        t = cur.get("/T")
        if t is not None:
            parts.append(str(t))
        cur = cur.get("/Parent")
    return ".".join(reversed(parts))


def check_checkbox(annot) -> bool:
    """Set /V and /AS on a checkbox widget using its actual on-state from /AP/N."""
    ap = annot.get("/AP", {})
    n_dict = ap.get("/N") if ap else None
    if not n_dict:
        return False
    on_state = next((k for k in n_dict.keys() if k != "/Off"), None)
    if not on_state:
        return False
    on_name = NameObject(on_state)
    annot[NameObject("/V")] = on_name
    annot[NameObject("/AS")] = on_name
    return True


def fill_pdf(profile_path: str, calc_path: str, blank_pdf_path: str, output_path: str):
    profile = json.loads(Path(profile_path).read_text())
    calc = json.loads(Path(calc_path).read_text())

    text_fields, checkbox_paths = build_text_fields(profile, calc)

    reader = PdfReader(blank_pdf_path)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)

    if "/AcroForm" not in writer._root_object:
        writer._root_object[NameObject("/AcroForm")] = DictionaryObject()
    if "/Fields" not in writer._root_object["/AcroForm"]:
        writer._root_object["/AcroForm"][NameObject("/Fields")] = ArrayObject()

    filled_text = 0
    filled_boxes = 0
    for page in writer.pages:
        if text_fields:
            writer.update_page_form_field_values(page, text_fields)
            filled_text += len(text_fields)
        if "/Annots" in page and checkbox_paths:
            for annot_ref in page["/Annots"]:
                annot = annot_ref.get_object()
                if annot.get("/FT") != "/Btn":
                    continue
                full = annotation_fullname(annot)
                if full in checkbox_paths:
                    if check_checkbox(annot):
                        filled_boxes += 1

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"SUCCESS: Filled {len(text_fields)} text fields, {filled_boxes} checkboxes")
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
