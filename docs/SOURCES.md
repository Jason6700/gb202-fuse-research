# Primary sources and prior research

Accessed and assembled 2026-11-14. Source code and product documentation may change; pin commit SHAs before citing measurements in formal reports.

1. **NVIDIA official RTX 5090 specifications:** https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/ — confirms product CUDA cores, VRAM and memory interface.
2. **NVIDIA RTX Blackwell architecture whitepaper:** https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf — full GB202 architecture, graphics cluster and cache configurations.
3. **NVIDIA open GPU kernel modules:** https://github.com/NVIDIA/open-gpu-kernel-modules — source for public portions of Linux kernel modules.
4. **NVIDIA GR control header:** https://github.com/NVIDIA/open-gpu-kernel-modules/blob/main/src/common/sdk/nvidia/inc/ctrl/ctrl2080/ctrl2080gr.h — public declarations for topology reporting.
5. **phiraml/gpu-unlock-blackwell:** https://github.com/phiraml/gpu-unlock-blackwell — related *but distinct* tensor speed-select feasibility research. Not a demonstration of SM/L2 unlocking.
6. **CUDA Runtime API, device properties:** https://docs.nvidia.com/cuda/cuda-runtime-api/structcudaDeviceProp.html — active device SM count and L2 cache size properties.

## Evidence caveats

The public Linux kernel source is not a complete implementation of all secure firmware behavior. A public control-interface declaration is not proof that a given retail Windows driver exposes it. Architecture diagrams describe design capacity rather than guaranteed post-fuse functional capacity for a particular silicon specimen.
