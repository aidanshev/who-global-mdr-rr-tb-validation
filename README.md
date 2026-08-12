# WHO Global MDR/RR-TB Forecast Validation

**Repository status:** `PARTIAL_FROZEN_CODE_MATERIALIZED`

National annual WHO MDR/RR-TB forecasting and strict surveillance-alert validation.

## Public-release policy

This repository is code/provenance-forward: raw patient-level surveillance data are excluded, third-party datasets are linked rather than mirrored, and image binaries are intentionally excluded. Source sites for visuals and data are recorded in `FIGURE_AND_IMAGE_PROVENANCE.md` and `DATA_SOURCES.md`.

Run before publishing:

```bash
python tools/public_release_audit.py
```

## Layout

- `code/` or `software/`: materialized analysis code
- `results/`: publication-safe aggregate results/receipts
- `manifests/`: identities and hashes without restricted raw data
- `docs/`: protocols/methods
- `REPOSITORY_STATUS.md`: completeness status

## Publication documentation

- `PUBLICATION_READINESS.md`: exact frozen-code/reproducibility boundary
- `CODE_AVAILABILITY.md`: evidence-matched manuscript Code Availability language
- `RELEASE_CHECKLIST.md`: completed and remaining archival steps
- `manifests/PROSPECTIVE_LOCK.json`: frozen prediction identity, source hashes, and no-retuning contract
- `CITATION.cff`: repository citation metadata

## Archival DOI

Do not create a final complete-code archival release until the missing hash-matched V2 development modules listed in `manifests/PROSPECTIVE_LOCK.json` are recovered. After recovery, audit the final tree, create an immutable GitHub Release, archive it with Zenodo or an equivalent preservation service, and add the DOI to this README, `CITATION.cff`, and the manuscript.
