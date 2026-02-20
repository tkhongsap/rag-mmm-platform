# Issue #87 — MS-7: Cloud Migration (Future — Placeholder)

**State:** Open
**Created:** 2026-02-19T09:57:08Z
**Updated:** 2026-02-19T09:57:08Z
**Labels:** —
**Assignees:** —
**Source:** https://github.com/tkhongsap/rag-mmm-platform/issues/87

---

## Objective

Move from local-disk infrastructure to cloud-ready deployment. This is a **placeholder milestone** — scope will be refined when MS-1 through MS-6 are complete.

## Key Results (Provisional)

| # | Key Result | Measure |
|---|-----------|---------|
| 1 | Qdrant runs as managed service | Qdrant Cloud instance provisioned, collections migrated |
| 2 | Assets served from object storage | Campaign images in S3/GCS, asset URLs point to cloud |
| 3 | Application is containerized | `Dockerfile` + `docker-compose.yml` build and run successfully |
| 4 | CI/CD pipeline exists | GitHub Actions workflow: lint → test → build → deploy |
| 5 | Environment config externalized | All secrets via env vars / secret manager, no local `.env` required |

## Provisional Tasks

- [ ] Containerize with Docker + docker-compose
- [ ] Migrate Qdrant to managed cloud instance
- [ ] Move assets to S3/GCS object storage
- [ ] Set up CI/CD (GitHub Actions: lint → test → build → deploy)
- [ ] Externalize all secrets via env vars / secret manager

## Deliverables (Provisional)

| File | Type |
|------|------|
| `Dockerfile` | New |
| `docker-compose.yml` | New |
| `.github/workflows/ci.yml` | New |
| Infrastructure configuration | TBD |

## Verification

```bash
docker-compose up --build
# Application accessible at configured port
# All integration tests pass against containerized services
```

## Dependencies

- **MS-6** (#86) — all tests passing and evaluation targets met before migration.

---
📋 Reference: [`docs/blueprint/milestones.md`](docs/blueprint/milestones.md) · [`docs/blueprint/team-execution-plan.md`](docs/blueprint/team-execution-plan.md)
