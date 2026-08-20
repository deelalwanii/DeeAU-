# DeeAU Transaction Audit Dashboard

A professional, web-based transaction audit workspace built with Streamlit, Pandas, NumPy and OpenPyXL.

## Features

- DeeAU branded administrator login.
- Excel `.xlsx` / `.xls` upload and worksheet selection.
- Automatic mapping of common transaction columns.
- Main audit groups with individually selectable sub-rules.
- Rule-driven exception testing.
- Transaction-level audit status, severity, rule IDs and remarks.
- Excel export named `transaction_audit.xlsx`.
- Report sheets: `Transaction Audit`, `Audit Summary`, `Rule Results`.
- Responsive CA-style dashboard layout.

## Run locally

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

The local development fallback login is the requested DeeAU administrator credential. For any shared/deployed instance, use `.streamlit/secrets.toml` or environment variables instead of keeping credentials in source control.

## Rule Book integration

The supplied Transaction Audit Rule Book was not available to the build environment in this session. The application therefore ships with a clearly separated starter rule catalog in `rules_catalog.py` and an extensible execution engine in `audit_engine.py`.

When the approved Rule Book is supplied, map each exact main audit / sub-audit to `AUDIT_GROUPS` and implement any rule-specific calculations in `AuditEngine._execute_rule`. Do not treat the starter rules as the client's final audit policy without that mapping.

## Recommended production hardening

- Replace local fallback credentials with Streamlit secrets or an identity provider.
- Add user roles (Admin / Reviewer / Read-only).
- Store audit logs and report hashes.
- Add configurable materiality thresholds and fiscal-year parameters.
- Add a Rule Book import/versioning screen.
- Add immutable execution IDs and reviewer sign-off fields.
- Encrypt uploaded files at rest if persisted.
