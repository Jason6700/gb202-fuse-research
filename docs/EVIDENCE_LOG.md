# Evidence ledger

Record falsifiable findings here. Keep claims and provenance separate.

| ID | Claim | Status | Evidence / source | What it does not show |
|---|---|---|---|---|
| E-001 | NVIDIA publishes 21,760 CUDA cores and 32 GB GDDR7 for RTX 5090 | Verified | [Official RTX 5090 specs](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/) | Defect status of disabled blocks |
| E-002 | Full GB202 includes 192 SMs | Verified | [NVIDIA Blackwell architecture](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf) | All 192 SMs usable on an individual retail die |
| E-003 | NVIDIA source headers describe read-only GR topology queries | Verified (header exists) | [ctrl2080gr.h](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/main/src/common/sdk/nvidia/inc/ctrl/ctrl2080/ctrl2080gr.h) | Userspace accessibility or raw fuse dump |
| H-001 | GB202 has a reversible override for fused-off SM/L2 | Hypothesis | No GB202-specific proof | Software-only feasibility |
| H-002 | Disabled SM/L2 blocks on the research card are functional | Hypothesis | No block-level manufacturing test records | Any successful activation |

## Measurement entry template

- Date (UTC):
- GPU model, PCI device ID, revision if known:
- OS and driver version:
- Tool and commit/release:
- Command / procedure:
- Direct observation:
- Interpretation:
- Alternative explanations:
- What would falsify the interpretation:
- Link to redacted machine-readable report:
