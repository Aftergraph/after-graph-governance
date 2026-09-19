# External Normative Source Profile 0.1

**Status:** Experimental interoperability profile  
**Owner:** Aftergraph Governance  
**Purpose:** bind an external normative source to an exact reproducibility anchor without creating a new standards ontology or granting authority.

## Boundary

This profile is metadata only. A record does **not** establish conformance, compliance, compatibility, security, production readiness, authority, admission, execution permission, or scientific validity.

The profile exists because Aftergraph already has separate owners for observed system reality (R.O.R.O.), compatibility/release intelligence (ARI/APC), authority/admission (AIE/Trust Gateway), durable execution (WORKS), and verification (native suites/Sentinel/Continuum). The only missing primitive was an exact, typed identity for the external normative input those systems may reference.

## Semantic foundation

The JSON profile deliberately reuses established web provenance semantics without requiring an RDF runtime:

| Profile field | Semantic correspondence |
|---|---|
| `canonical_uri` | DCAT Resource identity |
| `publisher` | `dcterms:publisher` |
| `release_version` | `dcat:version` |
| `status.raw` | source vocabulary / `adms:status`-style status |
| `published_at` | `dcterms:issued` |
| `previous_version_ref` | `dcat:previousVersion` / `prov:wasRevisionOf` |
| `replaces_ref` | `dcterms:replaces` |
| `primary_source_ref` | `prov:hadPrimarySource` |
| `digest` | checksum semantics compatible with supply-chain formats such as SPDX |

DCAT/PROV semantics are referenced, not copied into a new ontology.

## Invariants

1. At least one exact reproducibility anchor is required: `release_version`, `source_revision`, or `digest`.
2. `release_version` and `source_revision` are separate. A specification may have no publisher release number while still being exact at a source commit.
3. `status.raw` preserves the upstream publisher's wording. It is never silently replaced by an Aftergraph lifecycle label.
4. If the upstream source does not declare maturity/status, `status.source_declared=false` and `status.raw=null`.
5. `status.normalized`, when present, is secondary metadata only.
6. A protocol/specification and its TCK are distinct source records with distinct lifecycle/provenance.
7. Version/supersession links are only populated when explicitly evidenced by the upstream source.
8. The profile grants no authority.

## Pilot fixtures

The initial fixtures cover the five SSR-001 vectors:

- MCP 2026-07-28
- Agent Skills specification at exact source revision
- A2A 1.0.0 plus its separately versioned TCK
- OpenTelemetry GenAI semantic conventions with upstream `Development` status
- SLSA v1.2 with upstream `Approved` status

The fixtures are interoperability/conformance vectors for this metadata profile. They are not claims that the referenced Aftergraph implementations conform to those upstream sources.
