# Demo-only single-origin deployment: Next.js + FastAPI in one web service.
FROM node:22-bookworm-slim AS frontend_build
WORKDIR /srv/frontend
COPY frontend/package*.json ./
RUN npm install --no-audit --no-fund
COPY frontend/ ./
ENV NEXT_PUBLIC_API_URL=/api
RUN npm run build

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PROOFGRAPH_DB=sqlite:////data/proofgraph.db \
    PROOFGRAPH_STORAGE=/data/storage \
    NEXT_PUBLIC_API_URL=/api \
    PORT=10000
# Node binary + npm CLI are only needed to launch the built Next.js server.
COPY --from=frontend_build /usr/local/bin/node /usr/local/bin/node
COPY --from=frontend_build /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/npm
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm
WORKDIR /srv
COPY backend/requirements.txt /srv/backend/requirements.txt
RUN pip install --no-cache-dir -r /srv/backend/requirements.txt
COPY backend/ /srv/backend/
COPY --from=frontend_build /srv/frontend /srv/frontend
COPY deploy/start.py /srv/deploy/start.py
RUN mkdir -p /data/storage
EXPOSE 10000
CMD ["python", "/srv/deploy/start.py"]
