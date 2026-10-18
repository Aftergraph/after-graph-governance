# V2.1 TG ↔ WORKS Credential Boundary

Status: proposed deployment contract for Platform Convergence V2.1.

## Credentials

The execution-time Trust Gateway → WORKS correlation seam requires two independent server-held credentials:

- `WORKS_API_TOKEN`: stable service bearer, minimum 32 bytes.
- `WORKS_PLATFORM_BRIDGE_SECRET`: bridge binding secret, minimum 32 bytes.

Both values MUST be identical in the Trust Gateway and WORKS service environments.

They MUST NOT be:

- committed to git;
- written to application logs;
- returned by health endpoints;
- reused as worker enrollment tokens;
- exposed to browser/frontend code;
- persisted in evidence artifacts.

`WORKS_API_TOKEN` is not a WORKS worker enrollment JWT. Worker JWTs remain separately minted, scoped and restart/TTL bound.

## Production VDS locations

Current production topology:

- Trust Gateway env: `/root/agent-workforce/data/gateway.env`
- WORKS env: `/etc/works/works.env`
- Trust Gateway: `http://127.0.0.1:8800`
- WORKS: `http://127.0.0.1:18191`

Required TG variables:

```
WORKS_API_URL=http://127.0.0.1:18191
WORKS_API_TOKEN=<shared secret>
WORKS_PLATFORM_BRIDGE_SECRET=<shared secret>
```

Required WORKS variables:

```
WORKS_API_TOKEN=<shared secret>
WORKS_PLATFORM_BRIDGE_SECRET=<shared secret>
```

## Provisioning law

Provisioning MUST:

1. verify the exact target host before any mutation;
2. reuse a valid canonical value already present on one side;
3. refuse silent rotation when both sides contain different non-empty values;
4. refuse values shorter than 32 bytes;
5. generate 256-bit random values only when neither side has a value;
6. update files atomically with mode `0600`;
7. restart WORKS before Trust Gateway;
8. health-check both services;
9. roll both env files back if a post-write check fails;
10. record fingerprints/evidence only, never credential values.

The guarded implementation is maintained in Trust Gateway PR #121.

## Deployment ordering

Credential activation is valid only after the code that consumes the boundary is deployed:

1. WORKS #112: dedicated platform bearer + atomic execution-PDR correlation store.
2. Trust Gateway #119: V2.1 action-time chain and approval-time reauthorization.
3. Configure/synchronize both credentials.
4. Restart WORKS and verify `/healthz`.
5. Restart Trust Gateway and verify `/healthz`.
6. Execute an end-to-end V2.1 correlation smoke.
7. Verify signed evidence bundle and independent outcome projection remain distinct.

Do not provision credentials as a substitute for merging/deploying the consuming authority code.

## Rotation

Rotate both credentials as a coordinated maintenance operation:

- create replacement values without logging them;
- stop consequential V2.1 dispatch or place the seam in maintenance mode;
- write both services' env files;
- restart WORKS then TG;
- execute the same smoke/evidence gates;
- destroy superseded values after successful verification.

A partial rotation must fail closed.
