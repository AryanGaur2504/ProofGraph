# ProofGraph — Evidence Intelligence (SIH 2026 · SIH26263)

**AICTE ProofGraph: AI-Powered Application Validation, Document Authentication and Regulatory Compliance Verification**  
**Team:** Binary Battalion · **Theme:** Smart Automation · **Category:** Software

> **SYNTHETIC DEMONSTRATION DATA ONLY.** This is an independent Smart India Hackathon prototype. It is **not an official AICTE service** and contains **no real AICTE rules, thresholds, authority integrations, or institutional datasets**. No finding constitutes legal or regulatory proof of non-compliance. Human scrutiny and issuing-authority verification remain mandatory.

## What you can run

A local two-process application built with **FastAPI + SQLAlchemy/SQLite** and **Next.js + React**. No Docker, Redis, paid APIs, cloud databases, or runtime network integrations are required.

The **Interactive Demo** (`/demo`) calls the live sample-rule engine, shows exactly what was checked, and links findings to their source PDFs. The **Institution Portal** also provides downloadable synthetic PDFs to exercise the real upload, extraction, correction and revalidation workflow. The user interface includes a case queue, application checklist, interactive React Flow evidence graph, linked PDF viewer with region highlights, contradiction findings, historical change timeline, advisory metadata signals, synthetic source-status adapter, institution pre-flight portal, immutable versioned sample rules, human review decisions, deficiency/evidence PDF drafts, local evidence-only Q&A, audit-chain integrity check, and a 30-case synthetic evaluation dashboard.

### Prerequisites

- Python **3.11–3.13**, Node.js **20+**, npm **10+** (use a recent LTS release)
- `pip` and `npm` (first-time installation requires internet access or a local package cache; application runtime does not)
- Optional for image OCR: locally installed Tesseract; add `hin` language data for Hindi OCR. PDFs containing selectable text are extracted with PyMuPDF without OCR.

### Easiest Windows setup (corrected ZIP)

Extract the full ZIP, open its **AICTE-ProofGraph** folder and double-click `setup_windows.bat`, then `start_windows.bat`. The project includes both `requirements.txt` and `req.txt` at the **project root**, plus the original `backend/requirements.txt` and a backend alias. This removes ambiguity about the dependency file location. **`START_HERE.md` has the exact file tree and troubleshooting.**

From the project root, `py -m pip install -r requirements.txt` or `py -m pip install -r req.txt` resolves the original backend package list; installation into `backend/.venv` is recommended.

### Setup (Windows PowerShell)

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python seed.py --reset
cd ..\frontend
npm install
Copy-Item .env.example .env.local
cd ..
python run.py
```

### Setup (macOS / Linux)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python seed.py --reset
cd ../frontend
npm install
cp .env.example .env.local
cd ..
python run.py
```

**Access:** frontend **http://127.0.0.1:3000**, backend **http://127.0.0.1:8000**, interactive OpenAPI API docs **http://127.0.0.1:8000/api/docs**.

If you prefer separate terminals:

```bash
# Terminal 1, from backend/
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2, from frontend/
npm run dev
```

The package includes the generated demonstration database, synthetic PDF evidence, and `evaluation_labels.json`; re-seeding resets them to the known baseline. **Never run `python seed.py --reset` against valuable or real data.** A deliberate reset deletes the demo database tables and sample files.

### Demo accounts

All usernames use **`Demo@12345`** in the pre-seeded *fictional* environment.

| Username | Role | Capabilities |
|---|---|---|
| `officer` | Scrutiny Officer | View cases, revalidate, record human reviews, create report drafts |
| `senior` | Senior Officer | Officer actions, rule versioning, approve reports |
| `admin` | Admin | Full demo configuration and rule versioning |
| `auditor` | Auditor | Read-only access to case data and chained audit log |
| `institution` | Institution | Own institution's cases and pre-submission draft upload |

**These are demo credentials, not production credentials.** Replace the signing secret and establish a secure identity provider for real use.

## See what the app actually performs

Open **Interactive Demo** (`http://127.0.0.1:3000/demo`) and sign in as `officer`. Click **Run sample validation**:

- **Case #1:** Local rules compare **18 declared laboratories** with **15 inventory laboratories**, and compare the current **18** against the 2025 snapshot **12**. Open the findings, graph, and highlighted source PDFs. No authority is queried.
- **Case #2:** Extracted dates show an expired synthetic certificate, and hashing indicates re-use of a synthetic file across institutions. Official verification remains unavailable or visibly simulated.
- **Case #3:** A consistent sample passes the same checks with no active high-severity findings.

To prove that the functionality works with **new** files, open **Institution Portal**, create a Meridian draft, download the synthetic PDFs shown in the portal, upload the 18-lab form and 15-lab inventory, and inspect the newly generated contradiction. The correction form lets you fix a field with a mandatory audit reason and re-run checks.

For a click-by-click live presentation and troubleshooting, see **[`docs/TRY_THE_DEMO.md`](docs/TRY_THE_DEMO.md)** and the revised **[`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md)**. The system **does not** authenticate documents with real government authorities or make approval decisions.

## Test commands

```bash
cd backend
python -m pytest -q
```

The tests use a **temporary SQLite backup** of the seeded demo dataset, so review actions and tampering tests do not corrupt the starter database. Acceptance coverage includes evidence pages and bounding boxes, historical changes, unverified simulation, clean control cases, RBAC, cross-tenant evidence masking, local browser CORS, rule-version changes, audit tamper detection, real PDF upload/extraction, institution submission, draft PDF reports and evaluation labeling.

## Key APIs

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/auth/login` | Issue signed demo JWT |
| `GET` | `/api/cases` | Role-filtered case queue with optional filters |
| `GET` | `/api/cases/{id}` | Checklist, findings, docs, statuses and history |
| `POST` | `/api/cases/{id}/documents` | Protected PDF/image upload and local processing |
| `PATCH` | `/api/fields/{id}` | Correct an extraction with a recorded reason |
| `POST` | `/api/cases/{id}/revalidate` | Re-run deterministic demo rule pack |
| `GET` | `/api/cases/{id}/graph` | Serialized evidence nodes, typed edges, contradictions |
| `GET` | `/api/cases/{id}/patterns` | Cross-institution advisory patterns |
| `GET` | `/api/documents/{id}/file` | Protected document bytes |
| `GET` | `/api/documents/{id}/signals` | Offline advisory metadata/ELA-like diagnostics |
| `POST` | `/api/findings/{id}/review` | Human Confirm / Dismiss / Request / Escalate |
| `POST` | `/api/cases/{id}/verification/simulate` | Explicitly simulated outcome; never official |
| `GET` | `/api/rules` | Demo category checklists and versioned rules |
| `POST` | `/api/rules/{id}/version` | Immutable new version (authorized roles only) |
| `GET` | `/api/audit/verify` | Recompute hash chain and detect modifications |
| `GET` | `/api/evaluation` | Synthetic confusion matrix and demo metrics |
| `POST` | `/api/cases/{id}/reports` | Generate draft PDF report / clarification notice |
| `POST` | `/api/reports/{id}/approve` | Senior/Admin prototype release gate |
| `GET` | `/api/cases/{id}/ask?question=...` | Offline case-evidence Q&A with citations |

Full request and response schemas at `/api/docs` and OpenAPI JSON at `/api/openapi.json`.

## Architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/ERD.md`](docs/ERD.md), and [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md). The database holds **all specified minimum tables**, including `graph_nodes`, `graph_edges`, `rules`, `rule_versions`, `findings`, `finding_evidence`, `audit_events`, and `application_snapshots`. Storage is behind an extensible `StorageBackend` interface. Automated case checks use **versioned synthetic rule files** at [`backend/rules/sample_rules.json`](backend/rules/sample_rules.json).

## Security and scope

Protected API reads require JWTs; RBAC ensures an institution account cannot access another institution's files. Document storage uses randomized filenames, hashes, and path checking. Record-changing actions produce chained audit events, and the `Auditor` role is read-only. Field encryption uses Fernet **only when** `PROOFGRAPH_ENCRYPTION_KEY` is configured; the default demo mode intentionally uses visibly marked, non-sensitive test strings. For a meaningful security assessment read [`LIMITATIONS.md`](LIMITATIONS.md).

## Build verification performed in the authoring environment

- Python modules compile successfully.
- FastAPI smoke requests for login, cases, evidence graph, evaluation, verification patterns and report downloads succeeded.
- **14/14 Python acceptance and interactive-demo tests passed** using the seeded demo dataset.
- All 22 frontend TS/TSX files passed a TypeScript syntax parse; this is not a full typecheck or bundled Next.js build.
- **Next.js compilation and browser execution could not be confirmed** because the environment lacked npm registry DNS/connectivity. Run `npm install && npm run build` in a network-capable environment before presenting the frontend. Do not mistake successful static syntax parsing for a complete build test.

**No AICTE endorsement is implied.** No official government logo or seal is used.

## Updated, simplified UI

Use `/check` (sidebar **Upload & check**) for creating/opening cases, multi-document upload, automatic analysis, revalidation, findings and draft reports in one place. The landing dashboard now shows a four-step workflow, and advanced tools are collapsed into their own sidebar section. A persistent light/dark toggle is available in the top bar. See [UI_GUIDE.md](UI_GUIDE.md).
