# GSP/RM initialization and GB202 floorsweeping: public-source boundary

**Status (2026-11-18):** static source analysis, no GPU register interaction. This document distinguishes confirmed source code from architecture or Windows-specific hypotheses.

## Provenance and limitations

Pinned NVIDIA source revision: [`e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9`](https://github.com/NVIDIA/open-gpu-kernel-modules/tree/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9). Its [README](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/README.md#L1-L21) explicitly identifies **Linux open GPU kernel modules version 620.70.06**, which require corresponding GSP firmware and user-space components. The actual research machine runs **Windows NVIDIA driver 621.24**, so code-path equivalence is **not established**.

## Source-supported boundary timeline

| Stage | Evidence in pinned public Linux source | What is known / not known |
|---|---|---|
| 1. Prepare GPU firmware / initialization | [`kernel_gsp.c` image preparation and bootstrap](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/src/kernel/gpu/gsp/kernel_gsp.c#L6555-L6565); [image preparation](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/src/kernel/gpu/gsp/kernel_gsp.c#L6690-L6708) | The open kernel code includes image-handling/bootstrap routines; precise Windows 621.24/GB202 runtime sequence not inferred |
| 2. Verify / boot GSP-RM on supported paths | [`kernel_gsp.c` Booter comments](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/src/kernel/gpu/gsp/kernel_gsp.c#L6650-L6669); [GSP WPR metadata](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/arch/nvalloc/common/inc/gsp/gsp_fw_wpr_meta.h#L28-L35) | Source describes verified firmware/WPR handling for relevant boot paths, but does not disclose complete production firmware internals. [`kernel_gsp_tu102.c` boot description](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/src/kernel/gpu/gsp/arch/turing/kernel_gsp_tu102.c#L326-L334) is a **Turing** example, not independent proof of GB202 sequencing. |
| 3. Request floorsweeping static info | [`kernel_graphics.c` calls the internal RM control](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/src/kernel/gpu/gr/kernel_graphics.c#L1126-L1164) and [`NV2080_CTRL_CMD_INTERNAL_STATIC_KGR_GET_FLOORSWEEPING_MASKS`](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/src/kernel/gpu/gr/kernel_graphics.c#L1257-L1271) | **Confirmed source operation:** control call requests a mask structure. **Unknown:** implementation and ultimate origin of the returned masks, permissions on the retail Windows driver, and timing relative to physical fuse sampling |
| 4. Cache returned mask structure | [`kernel_graphics.c` copies the returned per-engine structure](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/src/kernel/gpu/gr/kernel_graphics.c#L1269-L1271) | This publicly visible path consumes already-constructed values; it is not a raw fuse read |
| 5. Serve topology queries from cached info | [GPC/TPC handlers](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/src/kernel/gpu/gr/kernel_graphics.c#L3544-L3643); [physical GPC mask handler](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/src/kernel/gpu/gr/kernel_graphics.c#L3874-L3881) | Logical/effective/physical **reporting** interfaces do not imply a writable hardware configuration |

## Source completeness

An indexed search of the pinned source for `NV2080_CTRL_CMD_INTERNAL_STATIC_KGR_GET_FLOORSWEEPING_MASKS` located the control declaration in `ctrl2080internal.h` and its client-side call in `kernel_graphics.c`. No production GB202 control **provider** implementation was confirmed from the published files searched. This is a documented inspection gap, **not proof** that the provider exists only in GSP firmware or that its behavior cannot be influenced.

The user's independent completed scans found:

- GB202-specific `fuse-register`: **9 untruncated matches**, eight GSP/SEC2 microcode-version register declarations plus one `gpuIsInternalSkuFuseEnabled_GB202` function that simply returns `NV_FALSE` ([source](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/src/kernel/gpu/arch/blackwell/kern_gpu_gb202.c#L355-L373)).
- Whole tree `direct-override`: **17 untruncated lexical matches**, all classified as display status, Tegra264 strap handling, or GB10B/GB10C status-offset references, **not** a GB202 SM/L2 override. See [FUSE_SCAN_REVIEW.md](FUSE_SCAN_REVIEW.md).

## Remaining questions

1. Identify documented code/data paths that supply the internal RM floorsweeping-mask response on production GB202; explicitly separate source unavailable to public inspection from negative evidence.
2. Determine when physical die fuse values are sampled relative to firmware-assembled and cached effective resource masks. **Currently unknown.**
3. Establish whether the Windows driver 621.24 offers any documented read-only APIs relevant to physical topology beyond CUDA's 170 SM and 96 MiB L2 reports. **Not established.**
4. Only if credible evidence emerges, assess whether any *reversible, authorized, software-only* change to effective SM/L2 configuration exists; **none demonstrated**.

**Safety boundary:** Keep all experiments on the primary RTX 5090 read-only. Do not attempt MMIO/register writes, fuse programming, firmware patching, undocumented GSP RPC calls, bootloader alterations or intrusive power/clock modifications.

**Conclusion:** The publicly demonstrated chain currently terminates at an internal RM static-information **request**, not at a known GB202 physical fuse reader or writable resource-disable mechanism.
