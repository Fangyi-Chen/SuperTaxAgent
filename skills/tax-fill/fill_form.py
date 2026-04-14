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


def _num(v) -> float:
    return v if isinstance(v, (int, float)) else 0.0


def sum_1099_interest(profile: dict) -> float:
    total = 0.0
    for item in profile.get("income", {}).get("otherIncome", []) or []:
        t = item.get("type", "")
        if t == "1099-INT":
            total += _num(item.get("box1_interest") or item.get("interest"))
        elif t == "1099-Consolidated":
            intblk = item.get("int") or {}
            total += _num(intblk.get("box1_interest") or intblk.get("interest"))
    return total


def sum_1099_div(profile: dict, ordinary: bool = True) -> float:
    total = 0.0
    for item in profile.get("income", {}).get("otherIncome", []) or []:
        t = item.get("type", "")
        if t == "1099-DIV":
            key = "box1a_ordinaryDiv" if ordinary else "box1b_qualifiedDiv"
            alt = "ordinaryDividends" if ordinary else "qualifiedDividends"
            total += _num(item.get(key) or item.get(alt))
        elif t == "1099-Consolidated":
            dblk = item.get("div") or {}
            key = "box1a_ordinaryDiv" if ordinary else "box1b_qualifiedDiv"
            total += _num(dblk.get(key))
    return total


def sum_capital_gains(profile: dict) -> float:
    """Sum net capital gain/loss from 1099-B (consolidated and standalone)."""
    total = 0.0
    for item in profile.get("income", {}).get("otherIncome", []) or []:
        t = item.get("type", "")
        if t == "1099-B":
            total += _num(item.get("netGainLoss") or item.get("gainLoss"))
        elif t == "1099-Consolidated":
            b = item.get("b") or {}
            gt = b.get("grandTotal") or {}
            total += _num(gt.get("gainLoss"))
    return total


def sum_1099_withheld(profile: dict) -> float:
    total = 0.0
    for item in profile.get("income", {}).get("otherIncome", []) or []:
        t = item.get("type", "")
        if t == "1099-Consolidated":
            for blk_key in ("int", "div", "b"):
                blk = item.get(blk_key) or {}
                total += _num(blk.get("box4_fedWithheld") or blk.get("fedWithheld"))
        else:
            total += _num(item.get("box4_fedWithheld") or item.get("fedWithheld"))
    return total


def line_value(calc: dict, line_key: str):
    """Read a value from calc['lines'][key] supporting common key variants."""
    lines = calc.get("lines") if isinstance(calc, dict) else None
    if not isinstance(lines, dict):
        return None
    for k in (line_key, line_key.lower(), line_key.upper()):
        if k in lines:
            return lines[k]
    return None


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

    # --- Derive figures from profile (fallback) ---
    wages = sum_w2(profile, "box1_wages")
    fed_w2 = sum_w2(profile, "box2_fedWithheld")
    fed_1099 = sum_1099_withheld(profile)
    interest = sum_1099_interest(profile)
    ord_div = sum_1099_div(profile, True)
    qual_div = sum_1099_div(profile, False)
    cap_gain = sum_capital_gains(profile)

    # Prefer calc.lines["N"] shape (emitted by /tax-calculate), then nested
    # shape, then raw profile fallback.
    def L(key, *nested_paths, default=None):
        v = line_value(calc, key)
        if v is not None:
            return v
        v = pick(calc, *nested_paths)
        return v if v is not None else default

    c_wages        = L("1a",  "income.wages",                              default=wages)
    c_1z           = L("1z",  "income.totalWages",                         default=wages)
    c_interest     = L("2b",  "income.interestIncome", "line2b_interest",  default=interest)
    c_qdiv         = L("3a",  "income.qualifiedDividends",                 default=qual_div)
    c_odiv         = L("3b",  "income.ordinaryDividends",                  default=ord_div)
    c_capgain      = L("7",   "income.capitalGains.netCapitalGains",       default=cap_gain)
    c_other        = L("8",   "income.otherIncome",                        default=0)
    c_total_income = L("9",   "income.totalIncome",                        default=None)
    c_adj          = L("10",  "adjustments",                               default=0)
    c_agi          = L("11",  "agi",                                       default=None)
    c_agi_page1    = L("11a", default=c_agi)
    c_agi_page2    = L("11b", default=c_agi)
    c_ded          = L("12",  "deduction.amount",                          default=None)
    c_ded12e       = L("12e", default=c_ded)
    c_qbi          = L("13a", default=0)
    c_sch1a        = L("13b", default=0)
    c_line14       = L("14",  default=c_ded)
    c_taxable      = L("15",  "taxableIncome",                             default=None)
    c_tax16        = L("16",  "tax.totalTax", "line16_tax",                default=None)
    c_line17       = L("17",  default=0)
    c_line18       = L("18",  default=c_tax16)
    c_ctc_nr       = L("19",  "credits.childTaxCredit.nonrefundable",      default=0)
    c_sch3         = L("20",  "credits.schedule3",                         default=0)
    c_line21       = L("21",  default=(_num(c_ctc_nr) + _num(c_sch3)))
    c_line22       = L("22",  default=None)
    c_line23       = L("23",  "otherTaxes",                                default=0)
    c_total_tax    = L("24",  "totalTax",                                  default=None)
    c_w2_wh        = L("25a", "payments.federalWithheld",                  default=fed_w2)
    c_1099_wh      = L("25b", "payments.withheld1099",                     default=fed_1099)
    c_25c          = L("25c", default=0)
    c_25d          = L("25d", default=(_num(c_w2_wh) + _num(c_1099_wh) + _num(c_25c)))
    c_eic          = L("27",  "payments.earnedIncomeCredit",               default=0)
    c_actc         = L("28",  "payments.additionalChildTaxCredit",         default=0)
    c_total_pay    = L("33",  "payments.totalPayments",                    default=None)
    c_refund       = L("34",  "refundOrOwed.amount",                       default=None)
    c_refund_35a   = L("35a", default=c_refund)
    c_owed         = L("37",  "line37_amountOwed",                         default=0)

    # Refund/owed type inference (for direct-deposit / amount-owed selection)
    c_refund_type = pick(calc, "refundOrOwed.type")
    if c_refund_type is None:
        if _num(c_refund) > 0:
            c_refund_type = "refund"
        elif _num(c_owed) > 0:
            c_refund_type = "owed"

    # --- Page 1 income (verified via probe) ---
    P1 = "topmostSubform[0].Page1[0]"
    fields[f"{P1}.f1_47[0]"] = fmt(c_wages)         # 1a
    fields[f"{P1}.f1_57[0]"] = fmt(c_1z)            # 1z
    fields[f"{P1}.f1_58[0]"] = fmt(0)               # 2a tax-exempt interest
    fields[f"{P1}.f1_59[0]"] = fmt(c_interest)      # 2b
    fields[f"{P1}.f1_60[0]"] = fmt(c_qdiv)          # 3a
    fields[f"{P1}.f1_61[0]"] = fmt(c_odiv)          # 3b
    fields[f"{P1}.f1_70[0]"] = fmt(c_capgain)       # 7
    fields[f"{P1}.f1_72[0]"] = fmt(c_other)         # 8
    fields[f"{P1}.f1_73[0]"] = fmt(c_total_income)  # 9
    fields[f"{P1}.f1_74[0]"] = fmt(c_adj)           # 10
    fields[f"{P1}.f1_75[0]"] = fmt(c_agi_page1)     # 11a

    # --- Page 2 (verified via probe) ---
    P2 = "topmostSubform[0].Page2[0]"
    fields[f"{P2}.f2_01[0]"] = fmt(c_agi_page2)     # 11b
    fields[f"{P2}.f2_02[0]"] = fmt(c_ded12e)        # 12e standard/itemized
    fields[f"{P2}.f2_03[0]"] = fmt(c_qbi)           # 13a
    fields[f"{P2}.f2_04[0]"] = fmt(c_sch1a)         # 13b
    fields[f"{P2}.f2_05[0]"] = fmt(c_line14)        # 14
    fields[f"{P2}.f2_06[0]"] = fmt(c_taxable)       # 15
    fields[f"{P2}.f2_08[0]"] = fmt(c_tax16)         # 16
    fields[f"{P2}.f2_09[0]"] = fmt(c_line17)        # 17
    fields[f"{P2}.f2_10[0]"] = fmt(c_line18)        # 18
    fields[f"{P2}.f2_11[0]"] = fmt(c_ctc_nr)        # 19
    fields[f"{P2}.f2_12[0]"] = fmt(c_sch3)          # 20
    fields[f"{P2}.f2_13[0]"] = fmt(c_line21)        # 21
    fields[f"{P2}.f2_14[0]"] = fmt(c_line22 if c_line22 is not None else (_num(c_line18) - _num(c_line21)))  # 22
    fields[f"{P2}.f2_15[0]"] = fmt(c_line23)        # 23
    fields[f"{P2}.f2_16[0]"] = fmt(c_total_tax)     # 24

    # Payments
    fields[f"{P2}.f2_17[0]"] = fmt(c_w2_wh)         # 25a
    fields[f"{P2}.f2_18[0]"] = fmt(c_1099_wh)       # 25b
    fields[f"{P2}.f2_19[0]"] = fmt(c_25c)           # 25c
    fields[f"{P2}.f2_20[0]"] = fmt(c_25d)           # 25d
    fields[f"{P2}.f2_23[0]"] = fmt(c_eic)           # 27 EIC
    fields[f"{P2}.f2_24[0]"] = fmt(c_actc)          # 28 ACTC
    fields[f"{P2}.f2_29[0]"] = fmt(c_total_pay)     # 33 total payments

    if c_refund_type == "refund":
        fields[f"{P2}.f2_30[0]"] = fmt(c_refund)        # 34 overpaid
        fields[f"{P2}.f2_31[0]"] = fmt(c_refund_35a)    # 35a refunded to you
        # Direct deposit routing/account
        dd = pi.get("directDeposit") or (profile.get("other") or {}).get("directDeposit") or {}
        if isinstance(dd, dict):
            if dd.get("routing"):
                fields[f"{P2}.RoutingNo[0].f2_32[0]"] = str(dd["routing"])
            if dd.get("account"):
                fields[f"{P2}.AccountNo[0].f2_33[0]"] = str(dd["account"])
            acct_type = (dd.get("type") or "").strip().lower()
            if acct_type == "checking":
                checkboxes.add(f"{P2}.c2_16[0]")
            elif acct_type == "savings":
                checkboxes.add(f"{P2}.c2_16[1]")
    elif c_refund_type == "owed":
        fields[f"{P2}.f2_35[0]"] = fmt(c_owed)          # 37 amount owed

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
