## Packaging correction (2026-10-22)

- Confirmed the previous ZIP did contain `backend/requirements.txt` but not a root-level `req.txt`; this caused confusing installation instructions.
- Added root `requirements.txt` and `req.txt`, plus `backend/req.txt`, all resolving to the same canonical backend dependency list.
- Added `setup_windows.bat`, `start_windows.bat`, and `VERIFY_PACKAGE.py` to simplify first-time installation and confirm critical files.
- Rewrote `START_HERE.md` with the exact extracted folder structure and PowerShell commands.
- Preserved the interactive demo, named ReactFlow import fix, synthetic database and evidence files.

# ProofGraph — Graph crash and interactive demo update

## Fixed

- `frontend/components/evidence-graph.tsx`: replaced invalid `ReactFlow` default import from `@xyflow/react` v12 with the named export, preventing the React "Element type is invalid" render crash.
- Improved graph inspection: selected nodes stay in view; use **View highlighted PDF** to open the source; focus on relevant evidence or expand all relationships.
- Corrected one misleading fictional fixture where a contractor's name was labeled as an institutional name. Regenerated the seeded database and matching sample report.
- Adjusted report pagination so the refreshed demo report no longer leaves an almost-empty second page.

## Added clarity and testable actions

- `Interactive Demo` sidebar entry (`/demo`) with three real backend sample validation runs, side-by-side values, detected findings and links to the source graph, documents and reviewer actions.
- Four-step Read → Compare → Explain → Resolve workflow on the homepage and case detail pages.
- **Run validation** button in the case workbench (calls existing permission-controlled `/api/cases/{id}/revalidate`).
- Four downloadable synthetic PDFs in the Institution Portal and `frontend/public/samples/` for an independent new-upload, contradiction and correction demonstration.
- Updated the judge guide, `docs/TRY_THE_DEMO.md`, README and setup instructions.
- Three new acceptance tests covering revalidation, clean-case results, and new PDF uploads plus resolution of a contradictory field.

## Verification status

- **14/14 backend tests passed** with a temporary SQLite test copy.
- PDF extraction tests confirmed all four new synthetic download fixtures are categorized and extracted correctly.
- All 22 frontend TypeScript/TSX files parse with the TypeScript compiler parser.
- **Full Next.js bundling and browser checks still need a local `npm install`, `npm run lint` and `npm run build`.** This environment cannot resolve the npm registry, so do not claim a verified production frontend build.

This is still a synthetic, human-in-the-loop demonstration, not official AICTE software.
