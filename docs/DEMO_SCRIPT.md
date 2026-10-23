# Five-minute ProofGraph judge script (updated interactive version)

**Precondition:** run the app with the local seeded synthetic dataset, log in as `officer` / `Demo@12345`, and open the **Interactive Demo** page. No official AICTE authority integration or real institutional data is involved.

**0:00–0:40 — Describe the problem.** “Institutions submit many PDFs, and data across forms, room inventories, certificates and prior submissions may disagree. ProofGraph is an evidence-linked scrutiny assistant, not an approval system.” Show the Overview: Read → Compare → Explain → Human review.

**0:40–1:50 — Run actual validation.** Select Scenario 1, then click **Run sample validation**. The frontend calls `POST /api/cases/1/revalidate` and refreshes the backend findings. Show the extracted values **18 labs declared**, **15 in room inventory**. The tool raises a contradiction backed by the two PDF fields.

**1:50–2:45 — Show original evidence.** Open Case #1 Findings: the discrepancy cites the source documents, page and bounding box, rule `SAMPLE-LAB-001` and suggested action. Go to Evidence Graph; click a relevant field node and use **View highlighted PDF**. Point out the distinct official, consistency, AI suspicion and manual-review statuses. Red graph edges are inconsistencies, not proof of fraud.

**2:45–3:20 — Historical intelligence.** In Case #1 History / Diff, show **12 labs in 2025 → 18 in 2026** and its request for sanctioned expansion evidence. Change is a review trigger, not proof of wrongdoing.

**3:20–4:05 — Advisory checks.** In Scenario 2 run the checker again. Explain expired-date detection and cross-institution PDF hash matches. Show `SOURCE_UNAVAILABLE` with the **SIMULATED** badge in Verification. Do not claim an issuing authority responded.

**4:05–4:30 — Clean control.** Run Scenario 3. The consistent seed does not produce active high-severity findings. Passing internal consistency does not establish authenticity.

**4:30–5:00 — Decisions and honest limits.** Click Request evidence on a Case #1 finding, enter a reason, then show the audit/review record. Export a clearly marked draft report. Mention that rules are versioned **SAMPLE** rules, 30 evaluation fixtures are synthetic, and any real deployment requires expert governance, independent evaluation and official integrations.

**Extra test if time permits:** Institution Portal → download the sample 18-lab application and 15-lab inventory → create a new draft → upload both → watch a new contradiction appear. This demonstrates that the pipeline works on user-supplied synthetic documents, not just seeded results. See `docs/TRY_THE_DEMO.md`.
