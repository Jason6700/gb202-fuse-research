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
- [x] Pin a public NVIDIA open-gpu-kernel-modules reference revision (`e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9`) and create a preliminary topology interface catalog. The local researcher's source checkout revision remains to be confirmed.
- [ ] Determine provenance of fuse-derived versus effective configuration. Public driver code now confirms retrieval of an internal floorsweeping-mask structure and subsequent queries from cached masks; the original provider remains unidentified.
- [ ] Document if raw fuse visibility exists for production GB202.
- [ ] Assess whether a reversible software-only SM/L2 override is actually possible.

**Working GB202 SM/L2 unlock: NOT demonstrated.**
