# UI Refresh — Guided Validation and Sample Source Records

## Experience changes

- Simplified global navigation to Home, Upload & validate, and Applications; optional advanced tools remain available.
- Removed the prominent demo marketing banner, demo navigation, walkthrough shortcuts, and demo-page access from the regular flow.
- Primary workspace now has three explicit steps: choose application, upload files, review result.
- Two separate sample-source document sets under `frontend/public/sample-packets/` with downloadable links on the upload page.
- Results show an easy-to-read finding summary, source values, direct access to the uploaded source PDF, the next action, and optional officer review.
- Moved technical checklists and evidence graphs into optional expanded sections.
- Updated the downloadable report to start with a readable summary; proof-linked details and status caveats are still present.
- Kept the light/dark mode switch in the top bar.
- Filtered 30 evaluation-fixture cases out of the regular user-facing case list (they remain available to the evaluation test harness).

## Safety and authenticity

G L Bajaj Institute of Technology and Management is named only within generated training records. The files are not institutional/authority records. No official issuer verification is performed. No non-compliance or forgery determination is automated.

## Test results

The new packet tests cover 3-PDF uploads using the consistent and anomalous sets and the resulting server-generated PDFs. Run `python backend/seed.py --reset` **only on disposable local test data**, then `PYTHONPATH=backend python -m pytest -q backend/tests` from the project root. Never reset a production database.
