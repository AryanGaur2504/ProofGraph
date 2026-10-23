# START HERE — AICTE ProofGraph (Windows)

This is a **local, independent prototype using synthetic demonstration data**. It is not an official AICTE application.

## First: extract the entire ZIP

In Windows File Explorer: right-click the ZIP → **Extract All** → open the **AICTE-ProofGraph** folder inside the extraction destination. Do not run project files directly from the ZIP preview.

After extraction, the folder should look like:

```text
AICTE-ProofGraph/
├── requirements.txt       ← root-level install file
├── req.txt                ← optional short alias
├── setup_windows.bat      ← first-time setup
├── start_windows.bat      ← launch the application
├── run.py
├── backend/
│   ├── requirements.txt   ← original dependency list
│   ├── req.txt            ← optional alias in backend/
│   ├── proofgraph.db      ← pre-seeded fictional data
│   └── app/
├── frontend/
│   ├── package.json
│   └── components/evidence-graph.tsx
└── docs/TRY_THE_DEMO.md
```

## Option A — easiest installation on Windows

1. Install **Python 3.11–3.13** and **Node.js 20+** and restart your terminal.
2. Double-click **`setup_windows.bat`** (installs Python and Node dependencies into the correct directories; requires internet access for installation).
3. Double-click **`start_windows.bat`** (uses the project's virtual environment; no PowerShell activation is required).
4. Open **http://127.0.0.1:3000/demo** after signing in with `officer` / `Demo@12345`.

## Option B — manual PowerShell commands, from this folder

```powershell
py -3 -m venv backend/.venv
.\backend\.venv\Scripts\python.exe -m pip install -r requirements.txt
cd frontend
npm install
cd ..
.\backend\.venv\Scripts\python.exe run.py
```

Both `pip install -r requirements.txt` and `pip install -r req.txt` work **from this root folder**. If you first `cd backend`, use `pip install -r requirements.txt` or `pip install -r req.txt` there. The ZIP contains all four paths so whichever filename you expected is available.

Before starting a new demo, you can run **`python VERIFY_PACKAGE.py`** to confirm the expected files and import fix are included. This does not replace the frontend build. For a full frontend check, run `cd frontend; npm run build` **after** installing npm dependencies.

## Show the functionality in 3 minutes

- **Scenario 1:** Compare **18 declared labs vs 15 inventoried** and **12 labs in the previous application**. Run validation, open the contradiction graph, and inspect the highlighted PDFs.
- **Scenario 2:** Inspect the **expired sample certificate** and an **identical document submitted by two fictional institutions**. External verification remains marked unavailable/simulated.
- **Scenario 3:** Show a **consistent control case** with no high-severity findings.
- **Fresh-document demo:** In the Institution Portal, upload the supplied sample PDFs from `frontend/public/samples/` into a new draft, then revalidate. See `docs/TRY_THE_DEMO.md`.

**IMPORTANT:** `backend/proofgraph.db` is pre-seeded. Avoid `python seed.py --reset` unless you intentionally want to erase and replace the synthetic demo database. This is a prototype; official source integrations are not implemented. See `LIMITATIONS.md`.

## Troubleshooting

- **Missing requirements:** Ensure you've opened the **inner** `AICTE-ProofGraph` folder and extracted the entire archive. You should see `requirements.txt` next to `run.py`, plus `backend/requirements.txt`.
- **`npm` not recognized:** Install Node.js 20+ and reopen PowerShell.
- **`No module named ...`:** Start through `start_windows.bat` or `backend/.venv/Scripts/python.exe run.py`, *not* an unrelated system Python.
- **`Element type is invalid` in EvidenceGraph:** This release uses `import {ReactFlow, ...} from '@xyflow/react'`. Stop the server, remove `frontend/.next` if present, and restart.
- **API unavailable:** Both frontend and backend must be running; see terminal output from the launcher.
