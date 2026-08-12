# Publication readiness

## Current release class

`PARTIAL_FROZEN_CODE_MATERIALIZED`

The repository contains an original frozen next-release evaluator, the exact prospective lock and its hashes, the no-retuning rule, public methods/provenance documentation, and release-safety tooling.

## Reproducibility boundary

The exact prospective lock identifies the missing model-development files and their SHA-256 hashes, including `v2_pipeline.py`, fixed-origin, ensemble, injection, surveillance-only, testing-adjusted, freeze, adjudication, and postprocessing stages. Those exact source files were not recoverable from the connected project materials during this publication pass and have not been reconstructed or replaced by new code.

Accordingly, this repository supports verification of the frozen prospective contract and evaluation procedure but is not yet a complete byte-for-byte model-development release.

## Publication safeguards

- The exact frozen prediction SHA-256 and no-retuning rule are retained in `manifests/PROSPECTIVE_LOCK.json`.
- `tools/public_release_audit.py` and the GitHub Actions workflow enforce the public-tree safety policy.
- No raw third-party pictures, report screenshots, or source datasets are redistributed.
- `CITATION.cff` does not claim a release version or DOI before a real immutable release exists.

## Remaining blockers to a complete code archive

1. Recover the exact hash-matched missing V2 source files listed in `manifests/PROSPECTIVE_LOCK.json`.
2. Select an explicit software license after ownership/upstream-license review.
3. Once the frozen code tree is complete, create an immutable GitHub Release and preservation DOI, then add that DOI to citation and manuscript metadata.

Until item 1 is resolved, describe this repository as a partial frozen-code/provenance deposit, not a complete reproducibility package.
