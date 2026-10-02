# Harness Verification Contract v1

Experimental cross-repository contract for independently verified harness evaluation outcomes.

## Boundary

WORKS owns evaluation orchestration. Sentinel is the independent verifier and producer of the receipt. Runtime may consume valid receipts as performance evidence. Governance owns promotion policy. Trust Gateway remains the execution-authority boundary.

A receipt is evidence only. It MUST NOT grant authority, promote a branch, or convert a shadow routing decision into production execution.

## Binding

Every receipt binds the exact routing decision, branch identity/hash, task class, outcome, evidence hash, and verification timestamp. Consumers fail closed on schema mismatch or identity mismatch.
