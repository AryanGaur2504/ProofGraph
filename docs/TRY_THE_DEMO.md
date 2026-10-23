# Show what ProofGraph actually does (interactive demo instructions)

ProofGraph is a **synthetic document cross-checking and human-review prototype**, not a government authentication or approval portal.

## Start

1. Install dependencies as shown in `START_HERE.md`, run `python run.py`, and open http://127.0.0.1:3000.
2. Log in as **officer** with **Demo@12345**.
3. Open the left-sidebar **Interactive Demo**. The live demo calls the existing FastAPI backend and reads its SQLite case records.

## Test 1: Run validation and see a contradiction

1. Select **Scenario 1** (Case #1).
2. Before you press the button, the page displays the already **seeded case** and its recorded findings.
3. Click **Run sample validation**. This sends `POST /api/cases/1/revalidate` to the local backend and refreshes the case result. There is no simulated AI response here: the installed deterministic validation rules execute.
4. Read the extracted fields: **Application Form = 18 laboratories**, **Room Inventory = 15**, and **Previous year = 12**.
5. Open **Evidence graph**. Click a field node, then click **View highlighted PDF** to inspect the actual extracted source region.
6. Open **Findings**. The discrepancy should cite the two document values, page references, sample rule `SAMPLE-LAB-001`, and separate verification / consistency / AI / officer statuses.
7. Open **History / Diff** to see 12 → 18 and the requested expansion evidence.
8. A reviewer can click **Request evidence**, explain why, and verify the action appears under **Audit / Reviews**. This changes the case's manual-review status; it is not an official decision.

## Test 2: Check expiry and document re-use

1. Select **Scenario 2** and click **Run sample validation**.
2. In **Findings**, review the expired fictional fire certificate and the building document re-used across two synthetic institutions.
3. In **Verification**, `SOURCE_UNAVAILABLE` is explicitly marked **SIMULATED**. This is *not* an issuing-authority verification.

## Test 3: Confirm no unnecessary high-severity warnings

1. Select **Scenario 3** and click **Run sample validation**.
2. The clean fixture contains consistent fields; no active high-severity findings should appear.
3. Clean consistency results are not equivalent to authentic documents or regulatory approval.

## Test 4: Validate entirely new PDFs (not just seed data)

1. Open **Institution Portal**. Choose **Meridian Institute of Technology**, **Extension of Approval**, then create a new draft.
2. Download the four synthetic examples listed on the Institution Portal, or from `frontend/public/samples/`.
3. In the new draft's **Documents** section, upload **Application_Form_18_Labs_DEMO.pdf** and **Room_Inventory_15_Labs_DEMO.pdf**. The backend parses the PDF text and automatically reruns its sample rules after each upload. You'll get a **Laboratories conflict** finding.
4. Add **Fire_Safety_Certificate_2028_DEMO.pdf** to satisfy the demo checklist.
5. Open **Documents**, select the inventory, and find the extracted `laboratories` field. Click **Edit**, change `15` to `18`, and enter a reason. Revalidation should clear the *active* laboratory contradiction. The correction and reason are audit logged. **Important:** only do this as a test of a *genuine correction*, not a way to conceal a discrepancy.
6. Alternatively, start a new synthetic draft with the **Room_Inventory_18_Labs_DEMO.pdf** file instead: both sources then agree. (New drafts can still have missing-document warnings until you upload the checklist files.)

## What is implemented and what is not

| Demonstrable | Status |
|---|---|
| Parse searchable PDF text, extract labeled fields and page coordinates | Implemented locally; scanned images depend on local OCR availability |
| Compare lab counts, relevant fields and sample checklists | Implemented with versioned **SAMPLE** rules |
| Detect expired dates | Implemented based on extracted dates, not official issuer status |
| Flag identical documents across institutions | Implemented with hashes; advisory only |
| Compare to previous application snapshots | Implemented where historical data exists |
| Show graph and highlighted pages | Implemented in React Flow + react-pdf; frontend build still requires local verification |
| Record reviewer actions with reasons; draft evidence-linked PDFs | Implemented |
| Check with a live issuing authority / certify AICTE approval / determine fraud | **Not implemented** |

## If the evidence graph crashes

The prior release used a default import of `ReactFlow` from `@xyflow/react` v12. That is not a valid default export. The corrected file is `frontend/components/evidence-graph.tsx` and must use a named import:

```tsx
import { ReactFlow, Background, Controls, MiniMap, MarkerType } from '@xyflow/react'
```

After replacing the project, stop the servers, run `npm install` from `frontend/`, then restart `python run.py`. If Next.js is still serving a stale compiled copy, remove `frontend/.next` and restart. **Do not delete the seeded database** when troubleshooting a frontend build.
