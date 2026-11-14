# Research roadmap

| Phase | Output | Success criterion | Risk |
|---|---|---|---|
| 0. Define boundaries | Safety and scope statement | No physical modifications or privilege writes on primary card | None |
| 1. Read-only baseline | Versioned NVIDIA-SMI + optional CUDA JSON | Reproducible active SM/L2 measurements and device metadata | Low |
| 2. Public code audit | Source symbol/path inventory with revision | Topology and initialization call graph | Low |
| 3. Topology mapping | Evidence table: physical vs logical vs effective | No conflation of post-floorsweep IDs with fuses | Low |
| 4. Override hypothesis | Candidate mechanism matrix | Each hypothesis has evidence, blocker, falsifier | Research only |
| 5. Feasibility decision | Technical report | Clearly supported yes/no/unknown for software-only override | Research only |
| 6. Optional experimental phase | Separate proposal for spare hardware | Isolated test system, reproducibility and rollback plan | Elevated; not part of current release |

## Hypotheses to test

**H1 — Post-fuse software shadow:** GB202 has a software-influencable effective SM/TPC/cache mask. Evidence needed: documented or independently verified GB202-specific path and actual read/write permissions. **Status: unverified.**

**H2 — Firmware-only change:** Some configuration is set by the GSP or related secure controller. Evidence needed: verified initialization sequence and authentication boundary; a bypass should never be presumed. **Status: unverified.**

**H3 — No software override:** Production fuse decisions are irrevocably latched into immutable hardware topology or protected against any software overrides. Evidence needed: architecture-specific documentation or strong negative evidence (negative tests alone cannot prove nonexistence). **Status: plausible but unverified.**

**H4 — Functional silicon availability:** A given retail GB202 has healthy disabled SM/L2 units. Read-only topology cannot decide this. **Status: unknown for individual devices.**

## Recommended first GitHub issues

1. `baseline: collect first RTX 5090 read-only report`
2. `source-audit: inventory floorsweep and topology interfaces`
3. `topology: distinguish logical vs physical GPC/TPC mapping`
4. `fuses: build evidence matrix for GB202 shadow and effective masks`
5. `firmware: document public GSP/security initialization boundaries`
6. `cache: inventory L2/LTC reporting and architecture limits`
7. `comparative: anonymous RTX 5090 mask survey protocol`
8. `paper: draft software-only feasibility assessment`

## Evidence required before any 'unlock' claim

- Independently verified **additional** active compute/cache beyond stock configuration.
- Demonstrated functionality, correctness and reproducibility, not a UI/property spoof.
- Clear provenance of software and device state before/after.
- Documented limitations across GPU revisions and firmware versions.
