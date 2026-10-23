# Deploy ProofGraph from GitHub (synthetic demo only)

> **Safety / limitations:** This is a publicly accessible, synthetic-data prototype with **shared demo credentials**. Do not upload real institutional applications or personal documents. Its rules are samples, not official AICTE requirements. Public hosting with a shared Admin password is not production-safe.

## Single-origin setup

`Dockerfile` builds Next.js and starts FastAPI privately on port 8000. Next.js listens on the host-provided `PORT` and rewrites `/api/*` requests to FastAPI. The UI uses `/api` on the same public origin; no `localhost` browser calls or separate API URL are required in production.

## Render: no Railway connection needed

1. Make sure this code is on the `main` branch of your GitHub `ProofGraph` repo.
2. Open [Render Dashboard](https://dashboard.render.com/), choose **New > Web Service**, and connect the GitHub repository. Choose **Docker** if asked.
3. Render will detect the repository's root `Dockerfile`; branch `main`, auto-deploy **On Commit**, health check path `/api/health`.
4. Add `PROOFGRAPH_JWT_SECRET` as a randomly generated secret (the `render.yaml` Blueprint can generate one automatically). Keep optional LLM off.
5. Wait for a successful deployment and visit its `*.onrender.com/demo` URL. Log in with the **fictional shared demo accounts** documented in `README.md`.
6. Future pushes/merges into `main` will trigger automatic redeploys when auto-deploy is enabled. See Render's deployments panel for build failures.

You may alternatively create a **New > Blueprint** from this repository to consume `render.yaml`.

## Data durability

The default/free configuration does **not** attach a persistent disk. The SQLite database and generated PDF fixtures live at `/data`, and on an empty filesystem the startup script recreates the synthetic test dataset. **Any uploaded files, edits, review actions and new cases will disappear on each restart/redeploy.** This is acceptable only for an isolated throwaway judging demo. If you need durable writes, use a paid persistent disk at `/data` or migrate to managed PostgreSQL plus object storage. Do not treat ephemeral SQLite as production persistence.

## Deployment verification checklist

- `/api/health` returns `{"status":"ok"}`.
- `/demo` opens without an `Element type is invalid` error.
- Officer demo credentials sign in; case #1 flags laboratories 18 vs 15.
- Evidence PDF loads through `/api/documents/{id}/file` via the same origin.
- After a new commit to `main`, Render shows a deployment associated with that commit.

## Other hosting

The same Dockerfile can run on platforms supporting container web services and writable temporary disk. For local development, continue to use `python run.py` and its separate `localhost` API.
