# PRD: MS-7 — Cloud Migration (Placeholder)

**Issue:** [#87](https://github.com/tkhongsap/rag-mmm-platform/issues/87)
**Branch:** `fix/issue-87-ms7-cloud-migration`
**Date:** 2026-02-20

## Introduction

MS-7 is a placeholder milestone that transitions the platform from local disk infrastructure to a cloud-ready deployment baseline. Work should start only after MS-1 through MS-6 are complete and stable.

## Goals

- Move vector and asset storage to managed cloud services.
- Containerize application services for repeatable deployment.
- Add CI/CD workflow for lint, test, build, and deploy stages.
- Externalize runtime configuration and secrets.

## User Stories

### US-001: Run Qdrant as managed cloud service
**Description:** As an operator, I want vector storage in managed infrastructure so local state is removed from app hosts.

**Acceptance Criteria:**
- [ ] Qdrant cloud instance is provisioned and reachable by API and background tasks.
- [ ] Existing `text_documents` and `campaign_assets` collections are migrated.
- [ ] Local paths fall back to cloud URLs from environment.

### US-002: Serve assets from object storage
**Description:** As a platform user, I want campaign assets served from cloud object storage for scalability and reliability.

**Acceptance Criteria:**
- [ ] Assets are uploaded to S3/GCS and URLs are surfaced from backend.
- [ ] `/api/assets/image/{path}` resolves to object storage URLs or signed links.
- [ ] Security policy prevents path traversal and unauthorized access.

### US-003: Containerize application
**Description:** As an operator, I want to run the stack from containers locally and in CI/CD.

**Acceptance Criteria:**
- [ ] `Dockerfile` builds backend image successfully.
- [ ] `docker-compose.yml` starts API, frontend, and supporting services.
- [ ] `docker-compose up --build` serves the platform at the configured port.

### US-004: Establish CI/CD pipeline
**Description:** As a release engineer, I want automated delivery from PR to deploy.

**Acceptance Criteria:**
- [ ] `.github/workflows/ci.yml` exists and runs lint, test, build, deploy steps.
- [ ] CI fails on lint/test failures.
- [ ] Deployment step deploys images or artifacts to target environment.

### US-005: Externalize secrets and config
**Description:** As a devops owner, I want no secrets committed and all runtime config driven by environment.

**Acceptance Criteria:**
- [ ] `.env` replaced by managed secret injection strategy for production.
- [ ] API keys, DB URLs, and model endpoints read from environment only.
- [ ] Local `.env` remains for development only.

## Functional Requirements

- FR-1: Add `Dockerfile` and `docker-compose.yml` for service composition.
- FR-2: Add `.github/workflows/ci.yml` with pipeline stages.
- FR-3: Replace hardcoded/local assumptions in config with cloud-ready environment variables.
- FR-4: Configure storage and asset serving integration with selected provider.
- FR-5: Validate deployment path with all existing integration tests passing.

## Non-Goals

- New feature development in RAG/MMM logic.
- Data model redesign or algorithm replacement.
- Full cost/security audit across all cloud resources.

## Technical Considerations

- This is a foundational infra milestone; keep implementation incremental with a migration plan.
- Ensure local development still works if docker-only deployment is incomplete.
- Provider choice (AWS vs GCP vs Azure) impacts API contracts and IaC tooling; decide before implementation.

## Files to Modify

| File | Change |
|------|--------|
| `Dockerfile` | New |
| `docker-compose.yml` | New |
| `.github/workflows/ci.yml` | New |
| Infrastructure config files | TBD |

## Success Metrics

- `docker-compose up --build` starts services cleanly.
- CI pipeline runs end-to-end with existing integration tests green.
- Qdrant and assets operate using cloud services in deployment mode.
- Sensitive values are not committed in repository.

## Verification

```bash
docker-compose up --build
```

## Open Questions

- Which cloud provider and container registry should be selected as the baseline for this milestone?
