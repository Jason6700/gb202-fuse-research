# GB202 Fuse & Floorsweeping Research

**Status: exploratory research. No working GB202 SM/L2 unlock is claimed or included.**

An independent, reproducible investigation into NVIDIA Blackwell **GB202** GPU hardware configuration, GPU floorsweeping, fuse-derived topology, and the feasibility of a **software-only, reversible** activation of currently disabled Streaming Multiprocessors (SMs) or L2 cache.

Initial research system: **ASUS ROG Astral GeForce RTX 5090 OC Edition**, Windows 11, NVIDIA GB202.

> This project is distinct from [phiraml/gpu-unlock-blackwell](https://github.com/phiraml/gpu-unlock-blackwell), which addresses a *tensor throughput speed-select restriction*, not an SM-count or L2-cache unlock.

## Research question

**Does production GB202 expose a software-accessible, privileged or unprivileged configuration override that can alter effective SM/TPC/GPC or L2 disable masks without changing permanent fuses or modifying hardware?**

Subquestions:

1. Which parts of the active topology can be observed through documented NVIDIA interfaces?
2. What evidence distinguishes physical hardware configuration, fuse-derived masks, and effective runtime masks?
3. Are any override/shadow mechanisms visible in publicly available source or firmware analysis?
4. If overrides exist, what protects them (GSP, signature enforcement, privilege controls, boot-time latching)?
5. Can a candidate be assessed rigorously *without* mistaking register visibility for unlock feasibility?

**A missing block is not necessarily a functional block.** A disable mask cannot establish whether silicon failed manufacturing tests or was removed for product segmentation.

## Scope and constraints

- **Software-only**, no board rework, soldering, voltage glitches, external programmers, power-limit bypasses, or eFuse programming.
- Phase 1 is **read-only** and can run on a primary gaming PC.
- Public evidence and offline static analysis take priority over any runtime experiments.
- No unsupported `BAR0` writes or unsigned firmware/kernel driver loading on the primary GPU.
- Any future state-changing tests require a separately documented safety review and spare test system.
- Publication of raw hardware identifiers (serial/UUID) is discouraged.

## Current known baseline

| Metric | RTX 5090 retail | Full GB202 design |
|---|---:|---:|
| Streaming Multiprocessors | 170 | 192 |
| CUDA cores | 21,760 | 24,576 |
| L2 cache | 96 MB (architectural specification) | 128 MB |

These figures describe published product/design configurations, **not** physical health of disabled units. See [sources](docs/SOURCES.md) and [architecture notes](docs/ARCHITECTURE.md). The CUDA API may report L2 in bytes; do not equate memory-unit conventions without documenting them.

## Repository layout

```
.
├── README.md
├── AGENTS.md
├── CONTRIBUTING.md
├── LICENSE
├── .github/
│   ├── ISSUE_TEMPLATE/research_task.md
│   └── workflows/python-tests.yml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── EVIDENCE_LOG.md
│   ├── RESEARCH_PLAN.md
│   ├── SAFETY.md
│   └── SOURCES.md
├── tools/
│   ├── collect_baseline.py      # read-only Windows NVIDIA-SMI report
│   ├── cuda_probe.cu            # optional CUDA SM/L2 report
│   └── source_audit.py          # offline search of public driver source
├── tests/
└── data/README.md
```

## Quick start (Windows 11, PowerShell)

The basic collector uses **Python 3.10+** and the NVIDIA driver-supplied `nvidia-smi`. No CUDA toolkit, experimental drivers, or administrator privileges are required for this basic step.

```powershell
python tools/collect_baseline.py --output reports/my-5090-baseline.json
```

The JSON report records GPU name, driver version, VBIOS version, memory quantity, and PCI device ID; **not** serial number or GPU UUID. Check the file for information you do not wish to publish before sharing it.

### Optional: measure active SM count and L2 cache

If the CUDA toolkit (`nvcc`) is installed, build the included **read-only** CUDA probe:

```powershell
nvcc -O2 -o cuda_probe.exe tools/cuda_probe.cu
.\cuda_probe.exe 0
python tools/collect_baseline.py --cuda-probe .\cuda_probe.exe --output reports/my-5090-with-cuda.json
```

This prints `cudaDeviceProp.multiProcessorCount` and `cudaDeviceProp.l2CacheSize`. These are **active/advertised** capabilities; neither tells you why a unit was disabled or reveals a raw fuse map. Treat them as a baseline only.

### Optional: offline NVIDIA source audit

Clone NVIDIA's *public source* separately (not bundled here):

```powershell
git clone --depth 1 https://github.com/NVIDIA/open-gpu-kernel-modules.git
python tools/source_audit.py open-gpu-kernel-modules --output reports/source-index.json
```

This generates keyword/path/line-number references, not executable patches or privileged GPU writes. Start with documented `GR_GET_*` topology interfaces and distinguish **logical post-floorsweep mappings** from raw physical masks.

## First milestones

1. Record first read-only GB202 baseline and Windows/driver environment.
2. Build a referenced inventory of topology-related NVIDIA interfaces.
3. Identify which publicly observable fields are physical, logical, fuse-derived, or unknown.
4. Document candidate override mechanisms and evidentiary gaps (including firmware privilege boundaries).
5. Publish a feasibility assessment with explicit falsification and validation criteria.

See the [research plan](docs/RESEARCH_PLAN.md), [evidence log](docs/EVIDENCE_LOG.md), and [GitHub publishing guide](docs/GITHUB_SETUP.md). Contributions should label statements as **verified**, **observed**, **inferred**, or **unverified hypothesis**.

## Not a fork or unlock release

This repository does not copy `phiraml`'s code and does not target their tensor speed-select restriction. Links to relevant prior work are credited in [sources](docs/SOURCES.md). No unlock is advertised or implied.

## License

MIT — see [LICENSE](LICENSE).
