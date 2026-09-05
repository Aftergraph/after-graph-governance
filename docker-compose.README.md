# Aftergraph Platform — Deployment Topology

> The 6 repos as one deployable platform. 3 runtime services + 2 docs repos.

## Services

| Service | Repo | Container | Port | Role |
|---|---|---|---|---|
| Trust Gateway | `trust-gateway-view` | `node:22-alpine` | 8800 | Control/enforcement plane + SPA + WORKS/AIE proxies |
| WORKS | `works-execution` | `golang:1.23` → distroless | 8080 | Durable execution plane |
| AIE | `aie` | `python:3.12-slim` | bridge CLI | Normative authority (invoked by TG) |
| GOV | `after-graph-governance` | docs only | — | Contract registry + frozen schemas |
| ISR | `intelligence-systems-research` | docs only | — | Research specs + conformance tests |

## Topology

```
Browser ──► TG :8800 (SPA + /v1/* + /v2/*)
                │
                ├──► WORKS :8080 (/v1/works, /v1/leases)  [works-client.js]
                ├──► AIE bridge CLI (aie_revalidate_bridge.py)  [aie-client.js]
                └──► AIE bridge CLI (aie_authority_bridge.py)  [132-authority-proxy.js]
```

The browser NEVER talks to WORKS or AIE directly. All cross-repo calls flow
through TG, preserving TG auth, tenant scoping, and fail-closed behavior.

## Quick start

```bash
# 1. Clone the 3 runtime repos as siblings
git clone https://github.com/Aftergraph/trust-gateway.git trust-gateway-view
git clone https://github.com/Aftergraph/works-execution.git works-execution
git clone https://github.com/Aftergraph/aie.git aie

# 2. Configure (no default secrets)
cp .env.example .env
# Edit .env: WORKS_API_TOKEN, WORKS_ENROLL_SECRET

# 3. Start
docker compose up -d

# 4. Verify
curl http://localhost:8800/healthz
curl http://localhost:8080/healthz
curl -H "Authorization: Bearer <tg-token>" http://localhost:8800/v2/executions
```

## Security posture

- All containers run as non-root (TG: `USER node`, WORKS: distroless, AIE: UID 1000).
- No default secrets — every credential is env-injected.
- Fail-closed: TG refuses to start consequential work if AIE revalidation is
  unreachable (`TG_AIE_FAIL_OPEN=false` is the production default).
- WORKS enrollment disabled unless `WORKS_ENROLL_SECRET` is set.
- Healthchecks on all 3 services; TG depends_on WORKS healthy.

## Contract conformance

All cross-repo calls conform to the frozen schemas in
`after-graph-governance/docs/contracts/frozen/` (SHA-pinned in
`works-execution/contracts/manifest.json`). Conformance tests:

| Contract | AIE tests | ISR tests |
|---|---|---|
| mission-state/1.0 | 6/6 | 6/6 |
| kernel.budget/1.0 | 6/6 | — |
| evidence.schema/1.1 | 5/5 | — |
| identity/1.0 | 7/7 | — |
| policy.token/1.0 | 7/7 | — |
