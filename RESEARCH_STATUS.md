# Research status — 2026-11-18

## Phase 0 — Repository and tooling
- [x] Define GB202-specific, software-only SM/L2 research scope.
- [x] Identify official product specifications and public topology interfaces.
- [x] Implement read-only NVIDIA-SMI and CUDA baseline tooling.
- [x] Publish repeatable Python checks.

## Phase 1 — Retail RTX 5090 baseline
- [x] Run the NVIDIA-SMI collector on the actual ASUS ROG Astral RTX 5090 OC.
- [x] Compile the CUDA probe using CUDA and Visual Studio 2026/MSVC.
- [x] Record a combined baseline locally on 2026-11-18 at 12:18:33 UTC.
- [x] Confirm 170 CUDA-reported SMs, 100,663,296 bytes (96 MiB) CUDA-reported L2, compute capability 12.0.
- [ ] Publish a redacted baseline artifact after an explicit privacy review.

The local baseline also records driver 621.24. The complete JSON, VBIOS value and PCI device metadata remain local, under ignored `reports/`; no personal device capture was committed to this public repository. These values are logical/advertised capabilities, **not** physical fuse measurements or functional tests of disabled hardware.

## Phase 2 onward
- [x] Pin a public NVIDIA open-gpu-kernel-modules reference revision (`e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9`) and create a preliminary topology interface catalog. The local researcher's source checkout has now been confirmed at the same SHA.
- [ ] Determine provenance of fuse-derived versus effective configuration. [GSP_FLOORSWEEP_BOUNDARY.md](docs/GSP_FLOORSWEEP_BOUNDARY.md) now traces the internal generic RM API, separately configured per-GPU GSP RPC control, GSP_INIT SKU/engine data, and the graphics mask consumer. The command-specific provider and origin of GB202 resource-disable masks remain unidentified; the source does **not** establish that the masks are assembled in firmware.
- [ ] Document if raw **SM/TPC/L2 resource-disable** fuse visibility exists for production GB202. A nine-hit path-filtered GB202 scan and 17-hit source-wide direct-override scan were completed; none identifies such a resource-enable control. A subsequently inspected GB202 GSP source file, **outside the nine-hit scan's path filters**, contains `kgspReadUcodeFuseVersion_GB202`, an actual **GSP microcode-version fuse** reader. Raw compute-resource fuse access remains unverified; see [source classification](docs/FUSE_SCAN_REVIEW.md) and [GSP/RM boundary](docs/GSP_FLOORSWEEP_BOUNDARY.md).
- [ ] Assess whether a reversible software-only SM/L2 override is actually possible. Next: trace the internal RM/GSP provider of floorsweeping-mask values, recognizing that NVIDIA's pinned *Linux 620.70.06* source is not identical to the Windows 621.24 driver tested.

**Working GB202 SM/L2 unlock: NOT demonstrated.**
