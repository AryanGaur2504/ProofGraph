# LIMITATIONS — important for judges and deployment reviewers

This is an independent **SIH demonstration prototype on wholly synthetic data**, not an AICTE-approved government system.

| Capability | State in prototype | What would be required for production |
|---|---|---|
| Application checklist | **Implemented**, using sample category config | Legal/regulatory expert mapping to specific current AICTE Approval Process Handbook sections and effective dates |
| PDF / text extraction | **Implemented** for selectable-text PDFs with PyMuPDF | Robust layout and language validation on realistic institutional document types |
| Image OCR | **Tesseract fallback** if binary/languages installed; offline and may miss fields | Benchmark Hindi/English OCR with representative documents; PaddleOCR is not bundled by default |
| Evidence graph | **Implemented** SQLite relational nodes/edges and React Flow UI source mapping | Scale and permission review for multi-user installations; richer relationships and entity resolution |
| Historical diff | **Implemented** for seeded snapshots and extracted current claims | Reliable prior-submission imports, sanctioned-change provenance and evidence ranking |
| Contradictions | **Implemented** for laboratory counts and select same-field mismatches, plus arithmetic demo | Expanded validators for every category after expert-reviewed rule packs |
| Cross-institution patterns | **Implemented**, SHA-256 and selected field matches; perceptual similarity only for comparable image kinds | Restrict appropriately under privacy/authorization policies; stronger false-positive evaluation |
| Image authenticity | **Advisory only**, EXIF presence, approximate recompression diagnostic, hashes and QR payload for images | Validated tamper detection, calibrated thresholds, provenance verification; never infer forgery from these weak signals |
| PDF digital signatures | **NOT VALIDATED**; UI explicitly shows `UNDETERMINED` | pyHanko integrated with trusted certificate chains, revocation and timestamp policy |
| Issuing-authority check | **SIMULATED** or `MANUAL_REQUIRED`; no government endpoint connected | Written source authorization and audited API agreements, accurate authority response parsing |
| Infrastructure vision | **Limited** to uploaded images, metadata hints and inventory/count contradictions | Expert-trained, independently tested CV detector with inspection escalation |
| LLM | **Disabled**; a provider-agnostic interface exists and local evidence-only template answers work | Secure provider client, prompt-injection defenses, constrained evidence citations, human review |
| Reports | **Implemented** draft PDFs and prototype approval gate | Formal document issuance workflow, signed release rules and official branding only if authorized |
| Evaluation | **30 seeded cases**, clean controls, exact fixture checks; results can be perfect | Independent held-out corpora, blinded human baselines, statistical confidence intervals, real operational timings |
| Translation | **Partial** English/Hindi sidebar labels; OCR supports Hindi only when local `hin` Tesseract pack is available | Fully translated UX, local language testing, assistive tech and accessibility audits |
| File processing | **Synchronous** FastAPI handling suitable for the demo | Durable job queue, retry isolation, memory/CPU resource controls, antivirus/content scanning |
| Retention | Policy is documented in `backend/governance.json`; automatic purge **disabled** | Legally approved schedule, secure data export and redaction/deletion governance |
| Encryption | Fernet-backed interface for sensitive fields if key supplied; without key explicitly **demo unencrypted** | Mandatory KMS/secrets management, TLS, disk encryption, key rotation and encryption by field class |
| JWT / RBAC | **Demo JWT/RBAC** and protected downloads | Verified MFA/SSO, fine-grained tenant scopes and independent penetration test |
| Audit | App-level SHA-256 linked events; detects normal row tampering | Immutable append-only storage, independent anchoring, monitoring, backups and clock trust |
| Migrations / concurrency | SQLAlchemy auto-create tables on startup, SQLite dev DB | Reviewed database migrations, transactional audit lock, PostgreSQL, concurrent writers, partitioned storage |
| Frontend QA | TSX **syntax parse passed** for revised pages; Next.js build **not tested** in authoring environment due blocked npm registry | `npm install`, `npm run lint`, `npm run build`, browser end-to-end tests |
| Official endorsement | **None**; neutral ProofGraph mark | Separate AICTE governance and permissions if formally adopted |

## Four different statuses are never merged

Every finding separates **OFFICIAL VERIFICATION**, **INTERNAL CONSISTENCY**, **AI SUSPICION (PRELIMINARY)** and **MANUAL REVIEW**. This prevents an internal match or an AI signal from being mislabeled as official authentication. The case **Attention Priority** is a transparent triage sum of High × 5, Medium × 3, Low × 1. These weights are prototype queue preferences, **not an AICTE threshold, official risk score, or fraud prediction**.

## Why the 30-case metrics are not an AICTE performance claim

The evaluation data is created by deterministic templates with known injected defects. Perfect template scores simply indicate that matching rules correctly identified expected defects in the toy distribution. No real-world recall, reduction in officer effort or fraud-detection efficacy can be inferred. The review-time comparison UI only calculates values the user directly enters; it does not manufacture measured times.

## Product ethics and next deployment gate

Before handling real applications, obtain authority approval for datasets and integration, specify the applicable rule and data-protection regime, commission external security/privacy/accessibility audits, and validate accuracy and workflow safeguards with scrutiny officers. No automatic rejection or regulatory enforcement is provided or appropriate.
