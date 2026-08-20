from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

ALIASES: Dict[str, List[str]] = {
    "transaction_id": ["transaction id", "transaction_id", "txn id", "txn_id", "voucher no", "voucher number", "document no", "document number"],
    "transaction_date": ["transaction date", "transaction_date", "date", "document date", "voucher date", "invoice date"],
    "posting_date": ["posting date", "posting_date", "entry date", "accounting date"],
    "amount": ["amount", "transaction amount", "net amount", "base amount", "value", "debit", "credit"],
    "invoice_no": ["invoice no", "invoice number", "invoice_no", "bill no", "bill number", "reference no", "reference number"],
    "vendor": ["vendor", "vendor name", "supplier", "supplier name", "party", "customer", "customer name"],
    "gstin": ["gstin", "gstin no", "gst number", "gst registration"],
    "gst_rate": ["gst rate", "gst %", "tax rate", "tax %", "gst_rate"],
    "gst_amount": ["gst amount", "tax amount", "igst", "cgst", "sgst", "gst_amount"],
    "description": ["description", "narration", "particulars", "remarks", "details"],
}


def _norm_col(name: str) -> str:
    return " ".join(str(name).strip().lower().replace("_", " ").split())


def normalize_transactions(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str], List[str]]:
    out = df.copy()
    mapping: Dict[str, str] = {}
    warnings: List[str] = []
    normalized_cols = {_norm_col(c): c for c in out.columns}
    for canonical, aliases in ALIASES.items():
        for alias in aliases:
            key = _norm_col(alias)
            if key in normalized_cols:
                mapping[canonical] = normalized_cols[key]
                break
        if canonical in mapping:
            out[canonical] = out[mapping[canonical]]
    if "transaction_id" not in mapping:
        warnings.append("Transaction ID column was not detected. Duplicate-ID and missing-ID rules may be skipped.")
    if "transaction_date" not in mapping:
        warnings.append("Transaction date column was not detected. Date-based rules may be skipped.")
    if "amount" not in mapping:
        warnings.append("Amount column was not detected. Amount-based rules may be skipped.")
    for c in ["transaction_date", "posting_date"]:
        if c in out.columns:
            out[c] = pd.to_datetime(out[c], errors="coerce")
    if "amount" in out.columns:
        out["amount"] = pd.to_numeric(out["amount"], errors="coerce")
    if "gst_rate" in out.columns:
        out["gst_rate"] = pd.to_numeric(out["gst_rate"], errors="coerce")
    if "gst_amount" in out.columns:
        out["gst_amount"] = pd.to_numeric(out["gst_amount"], errors="coerce")
    return out, mapping, warnings


class AuditEngine:
    def __init__(self, groups: List[dict]):
        self.groups = groups
        self.rules = {rule["id"]: rule for group in groups for rule in group["rules"]}

    def run(self, df: pd.DataFrame, selected_rules: List[str]) -> Tuple[pd.DataFrame, List[dict]]:
        result = df.copy()
        result["Audit Status"] = "Pass"
        result["Audit Severity"] = "None"
        result["Audit Rule IDs"] = ""
        result["Audit Remarks"] = ""
        rule_results = []

        for rule_id in selected_rules:
            rule = self.rules[rule_id]
            mask, remark, severity = self._execute_rule(result, rule_id)
            mask = pd.Series(mask, index=result.index).fillna(False).astype(bool)
            count = int(mask.sum())
            if count:
                result.loc[mask, "Audit Status"] = "Exception"
                result.loc[mask, "Audit Rule IDs"] = result.loc[mask, "Audit Rule IDs"].apply(lambda x: self._append(x, rule_id))
                result.loc[mask, "Audit Remarks"] = result.loc[mask, "Audit Remarks"].apply(lambda x: self._append(x, remark))
                result.loc[mask, "Audit Severity"] = result.loc[mask, "Audit Severity"].apply(lambda x: self._max_severity(x, severity))
            rule_results.append({
                "Rule ID": rule_id,
                "Main Audit": rule["group"],
                "Audit Procedure": rule["name"],
                "Severity": severity,
                "Exception Count": count,
                "Status": "Exception Found" if count else "No Exception",
            })

        return result, rule_results

    @staticmethod
    def _append(current: str, new: str) -> str:
        return new if not current else f"{current} | {new}"

    @staticmethod
    def _max_severity(current: str, new: str) -> str:
        rank = {"None": 0, "Low": 1, "Medium": 2, "High": 3, "Critical": 4}
        return new if rank.get(new, 0) > rank.get(current, 0) else current

    def _execute_rule(self, df: pd.DataFrame, rule_id: str):
        if rule_id == "DATA-001":
            if "transaction_id" not in df.columns:
                return np.zeros(len(df), dtype=bool), "Transaction ID is unavailable for testing", "High"
            mask = df["transaction_id"].isna() | df["transaction_id"].astype(str).str.strip().eq("")
            return mask, "Missing Transaction ID", "High"

        if rule_id == "DATA-002":
            if "transaction_date" not in df.columns:
                return np.zeros(len(df), dtype=bool), "Transaction date is unavailable for testing", "High"
            return df["transaction_date"].isna(), "Missing or invalid transaction date", "High"

        if rule_id == "DATA-003":
            if "amount" not in df.columns:
                return np.zeros(len(df), dtype=bool), "Amount is unavailable for testing", "High"
            return df["amount"].isna(), "Missing or non-numeric transaction amount", "High"

        if rule_id == "DUP-001":
            if "transaction_id" not in df.columns:
                return np.zeros(len(df), dtype=bool), "Transaction ID is unavailable for duplicate testing", "High"
            valid = df["transaction_id"].notna() & df["transaction_id"].astype(str).str.strip().ne("")
            mask = valid & df["transaction_id"].duplicated(keep=False)
            return mask, "Duplicate Transaction ID", "High"

        if rule_id == "DUP-002":
            if "invoice_no" not in df.columns:
                return np.zeros(len(df), dtype=bool), "Invoice/reference number is unavailable for duplicate testing", "Medium"
            valid = df["invoice_no"].notna() & df["invoice_no"].astype(str).str.strip().ne("")
            mask = valid & df["invoice_no"].duplicated(keep=False)
            return mask, "Duplicate invoice/reference number", "Medium"

        if rule_id == "DATE-001":
            if "transaction_date" not in df.columns:
                return np.zeros(len(df), dtype=bool), "Transaction date is unavailable for future-date testing", "Medium"
            today = pd.Timestamp.now().normalize()
            mask = df["transaction_date"].notna() & (df["transaction_date"].dt.normalize() > today)
            return mask, "Transaction date is in the future", "Medium"

        if rule_id == "DATE-002":
            if not {"transaction_date", "posting_date"}.issubset(df.columns):
                return np.zeros(len(df), dtype=bool), "Transaction date and posting date are both required", "Medium"
            mask = df["transaction_date"].notna() & df["posting_date"].notna() & (df["transaction_date"] > df["posting_date"])
            return mask, "Transaction date is after posting date", "Medium"

        if rule_id == "AMT-001":
            if "amount" not in df.columns:
                return np.zeros(len(df), dtype=bool), "Amount is unavailable for zero-value testing", "Low"
            mask = df["amount"].fillna(np.nan).eq(0)
            return mask, "Zero-value transaction", "Low"

        if rule_id == "AMT-002":
            if "amount" not in df.columns:
                return np.zeros(len(df), dtype=bool), "Amount is unavailable for outlier testing", "Medium"
            vals = df["amount"].dropna().abs()
            if len(vals) < 8:
                return np.zeros(len(df), dtype=bool), "Insufficient population for statistical outlier test", "Medium"
            q1, q3 = vals.quantile([0.25, 0.75])
            iqr = q3 - q1
            threshold = q3 + (1.5 * iqr)
            mask = df["amount"].abs() > threshold
            return mask, f"Amount exceeds statistical outlier threshold ({threshold:,.2f})", "Medium"

        if rule_id == "GST-001":
            if not {"gst_rate", "gst_amount"}.issubset(df.columns):
                return np.zeros(len(df), dtype=bool), "GST rate and GST amount columns are required", "Medium"
            mask = (df["gst_rate"].fillna(0).eq(0) & df["gst_amount"].fillna(0).ne(0)) | (df["gst_rate"].fillna(0).ne(0) & df["gst_amount"].fillna(0).eq(0))
            return mask, "GST rate and GST amount appear inconsistent", "Medium"

        if rule_id == "GST-002":
            if "gst_rate" not in df.columns:
                return np.zeros(len(df), dtype=bool), "GST rate column is unavailable", "Low"
            mask = df["gst_rate"].notna() & ((df["gst_rate"] < 0) | (df["gst_rate"] > 100))
            return mask, "GST rate is outside 0–100%", "High"

        if rule_id == "PARTY-001":
            if "vendor" not in df.columns:
                return np.zeros(len(df), dtype=bool), "Vendor/party column is unavailable", "Medium"
            mask = df["vendor"].isna() | df["vendor"].astype(str).str.strip().eq("")
            return mask, "Missing vendor/customer/party name", "Medium"

        if rule_id == "PARTY-002":
            if "gstin" not in df.columns:
                return np.zeros(len(df), dtype=bool), "GSTIN column is unavailable", "Medium"
            gstin = df["gstin"].fillna("").astype(str).str.replace(" ", "", regex=False).str.upper()
            mask = gstin.ne("") & ~gstin.str.match(r"^[0-9]{2}[A-Z0-9]{5}[0-9]{4}[A-Z][A-Z0-9][Z][A-Z0-9]$", na=False)
            return mask, "GSTIN format appears invalid", "High"

        if rule_id == "TEXT-001":
            if "description" not in df.columns:
                return np.zeros(len(df), dtype=bool), "Description/narration column is unavailable", "Low"
            mask = df["description"].isna() | df["description"].astype(str).str.strip().eq("")
            return mask, "Missing transaction description/narration", "Low"

        return np.zeros(len(df), dtype=bool), "Rule not implemented", "Low"
