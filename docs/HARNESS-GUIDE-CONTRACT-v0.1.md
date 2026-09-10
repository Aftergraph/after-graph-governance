# Harness Guide Contract — v0.1

Status: adopted 2026-09-10. Applies to every repository-level `AGENTS.md` in the Aftergraph polyrepo.

## Why this exists

An agent arriving in a repository should not have to rediscover the repository. Before this contract, only
two of the twenty-four repositories carried a repository-level guide, and the verification command for the
rest was reconstructed by trial and error on every visit. That rediscovery is measurable, and it was
measured before any guide existed: 35.4% of repository-scoped agent sessions ran the repository's own
verification command, and 48.8% edited files without ever running it.

The guide is a feedforward control. Its only job is to remove that rediscovery. Everything else attributed
to "better agents" is downstream of it and should be measured separately.

## What a repository guide must contain

1. **Role and purpose** as declared by the workspace contract, not as guessed from the name.
2. **Local conventions** — the commands actually present on disk in that repository. A command that is not
   in the repository is not written down.
3. **Executed verification** — the command that was actually run, its result, and the exact SHA, quoted from
   `CI_RESULTS.json`. A repository with no recorded execution says so explicitly; no build or test command
   is invented for it.
4. **Inherited rules** from `/root/workspace/aftergraph/AGENTS.md`, unchanged, so the local file never
   contradicts the workspace contract.
5. **A Ratchet section** — see below. It starts empty and is the only hand-edited part.
6. **Guide hygiene rules**, including the instruction to delete anything automation now enforces.

## Generator guarantees

`scripts/gen_repo_guides.py` produces the file. Each guarantee below is pinned by a test in
`scripts/test_repo_guide_generation.py`; if a guarantee is dropped, the test fails.

| guarantee | test |
|---|---|
| Manifest and Makefile commands are taken verbatim from the repository | `test_package_manifest_commands_are_used_verbatim`, `test_makefile_target_is_used_when_no_manifest` |
| A repository without a recorded sensor is told so, and no command is invented | `test_repository_without_sensor_is_not_given_an_invented_command` |
| Recorded evidence is quoted with its result and exact SHA | `test_recorded_evidence_is_quoted_with_its_sha` |
| Ratchet rules survive regeneration, exactly once | `test_ratchet_rules_survive_regeneration` |
| A hand-written guide is never overwritten | `test_hand_written_guide_is_never_overwritten` |
| A generator-owned guide is only replaced with `--force` | `test_generated_guide_is_replaced_only_with_force` |

Usage:

```bash
python scripts/gen_repo_guides.py --root /path/to/workspace            # create missing guides only
python scripts/gen_repo_guides.py --root /path/to/workspace --force    # refresh command blocks, keep Ratchet
python scripts/gen_repo_guides.py --root /path/to/workspace --dry-run  # report what would change
```

It writes `GUIDE_GENERATION_EVIDENCE.json` in the workspace root: one row per repository, with the base SHA,
the live SHA, the branch, the commands detected, the number of executed-verification rows found, and the
number of Ratchet rules preserved.

## The Ratchet

The Ratchet section is the only part of a guide a human or agent edits by hand, and it is the part that
compounds. Rules enter it one way only: an agent fails in that repository in a way that was not prevented,
and the fix is written down.

Each rule must:

- trace to **one observed failure** in that repository — not a hypothetical, not a best practice;
- be dated, so stale guidance is identifiable;
- be fixed at the **strongest layer that prevents recurrence**:

```text
memory note  <  prompt instruction  <  guide rule  <  sensor (test/lint/schema)  <  environment constraint
```

The ladder matters more than the rule. If a rule can be checked without human judgement, it does not belong
in the guide — it belongs in a CI step, a schema, or a permission. **A guide that keeps growing is a guide
whose sensors are missing.** Declining growth in the Ratchet, not a large Ratchet, is the signal that the
harness is maturing.

### Why the Ratchet must survive regeneration

The first version of the generator overwrote the whole file on `--force`, which silently destroyed every
accumulated rule. That is worse than having no Ratchet at all: it makes the guide layer look like it is
learning while discarding what it learned. Regeneration now carries the existing rule body across, strips
only the fixed instruction lines, and records how many rules it preserved in the evidence file. This is the
first rule the contract itself produced, and it is enforced by a test rather than by a sentence.

## Measurement

`scripts/harness_scorecard.py` computes the guide-layer metrics from local evidence and appends a row to
`SCORECARD_HISTORY.jsonl` so growth is visible over time. It never asserts a number it did not compute.

```bash
python scripts/harness_scorecard.py --root /path/to/workspace --write
```

| metric | source | healthy direction |
|---|---|---|
| guide coverage | inventory + file check | up, then flat |
| ratchet rules recorded | all guides | up slowly, growth rate declining |
| guide staleness | file mtime | down |
| sensor coverage | `CI_RESULTS.json` | up |
| evidence freshness | recorded SHA vs live HEAD | current up, stale down |
| not instrumented | declared explicitly | shrinks honestly |

Thresholds adopted with this contract:

```text
guide coverage >= 95% and not falling
every repository with a Hard surface has at least one recorded executed sensor
evidence current at live HEAD for every repository touched in the last 14 days
ratchet rule growth present but declining
```

## Scope: what lives here and what does not

Portable, and therefore in this repository:

- `scripts/gen_repo_guides.py` — guide generation from the workspace inventories;
- `scripts/harness_scorecard.py` — coverage, sensor and freshness metrics;
- `scripts/test_repo_guide_generation.py` — the contract tests.

Host-local, and deliberately **not** here, because they read the agent runtime rather than the repositories:
the failure classifier and the discovery-cost instrument read the Hermes session store, and the
publish/merge tooling operates on this host's checkouts. They are documented in the workspace measurement
note and are not part of the governance contract.

## What this contract cannot do

A guide is only useful if it is read. Nothing here verifies that an agent opened the file, so an improvement
in the metrics is evidence that the harness is maintained — not evidence that any particular session was
better. Local green output proves only that a command produced that result at that SHA; it does not
establish production readiness, and no guide may claim otherwise.
