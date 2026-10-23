# ProofGraph v1.0: simple guided user interface

This is a synthetic demonstration, not an official AICTE portal. Do not upload real documents.

## Where do I upload files?

1. Sign in with a sample account.
2. Click **Upload documents** in the top bar or **Upload & check** in the sidebar.
3. In Step 1, create an application (or select an existing case).
4. In Step 2, click the large **Click here to choose your files** upload area. Select multiple PDFs/images.
5. You can leave document type on **Auto-detect**, or choose a type for better labeling. Click **Upload & analyze**.
6. Step 3 shows active findings, missing/expired checklist items, and direct links to original evidence.

## Where do I recheck?

On the same **Upload & check** screen, Step 3 has a prominent **Recheck now** button for officer accounts. Institution accounts get an automatic check with each upload, plus **Refresh results** to update the page. You can add more files to the same case in Step 2.

## What do the results mean?

A finding lists what two pieces of evidence say, the sample rule that raised the issue, and a link to inspect the PDF. The application does **not** authenticate documents with real issuing authorities, conclude fraud, or decide compliance. Officers are responsible for review decisions.

## What are the other screens?

- **Home**: simple four-step introduction and recent applications.
- **Upload & check**: main everyday workflow, new or existing case.
- **Applications**: a searchable, filtered list of cases.
- **Try demo cases**: predefined 18-vs-15 laboratories, expiry/duplicate signals, and clean-control case.
- **Advanced tools**: evaluation metrics, editable demo rule versions, audit history, and a demonstration guide.
- **Detailed case**: the most-used tabs are Overview, Files & upload, Results & decisions, and Evidence Graph. The other case features are behind **More tools**.

## Light or dark mode

Click the moon/sun button in the top navigation. Your choice is saved in browser local storage. If no choice is saved, the browser's system preference is used.

## Role permissions

Institution accounts can edit their drafts and upload synthetic evidence, but cannot call officer-only revalidation or record officer decisions. Their document uploads automatically run checks. Auditors are read-only. Scrutiny officers, senior officers, and administrators can revalidate, generate draft reports, and record evidence-linked decisions.

## Deployment status

The codebase includes a single-origin Dockerfile for Next.js and FastAPI and an auto-deploy-capable Render service. Running a full frontend production build and browser UX test is still required before treating this UI update as production-verified. The free demo's SQLite storage is ephemeral.
