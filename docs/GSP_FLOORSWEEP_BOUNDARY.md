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

**Conclusion:** The publicly demonstrated chain currently terminates at an internal RM static-information **request**, not at a known GB202 **SM/TPC/L2 resource-disable** fuse reader or writable resource-disable mechanism. A separate GB202 microcode-version fuse reader is documented below.

## Deeper trace: API dispatch and the limit of the public source (2026-11-18)

This supplements the earlier timeline. Source links are pinned to the same NVIDIA revision.

### Two RM API interfaces must not be conflated

1. [`rmapi.c` lines 168–224](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/src/kernel/rmapi/rmapi.c#L168-L224) initializes the **generic/internal** `RM_API` interfaces, assigning `pRmApi->Control = rmapiControl`. Its `rmapiGetInterface(RMAPI_GPU_LOCK_INTERNAL)` returns a pointer to the internal API dispatch table. This is the API called by `kgraphicsLoadStaticInfo_KERNEL` when requesting `KGR_GET_FLOORSWEEPING_MASKS`; it is **not itself a direct call to `rpcRmApiControl_GSP`**.
2. [`rpc_common.c` lines 54–80](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/src/kernel/rmapi/rpc_common.c#L54-L80) configures a **per-GPU physical RM API**: when `IS_GSP_CLIENT(pGpu)` is true, its `Control` method is assigned `rpcRmApiControl_GSP`.
3. [`rpc_global_enums.h` lines 75–87](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/inc/kernel/vgpu/rpc_global_enums.h#L75-L87) defines the `GSP_RM_CONTROL` RPC function (76). [`kernel_gsp.c` lines 317–325](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/src/kernel/gpu/gsp/kernel_gsp.c#L317-L325) logs/decode-displays its `cmd` and `paramsSize` payload metadata.
4. [`rpc.h` lines 215–238](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/inc/kernel/vgpu/rpc.h#L215-L238) shows one GPU RPC control helper routing firmware-client operations through the per-GPU physical RM API or another RPC DMA wrapper. This supports the existence of an RPC transport mechanism.

**Important limitation:** these files demonstrate a general RM-to-GSP transport architecture, but **do not by themselves prove every hop** from the `rmapiControl` request in `kgraphicsLoadStaticInfo_KERNEL` to the firmware implementation of that *specific* internal floorsweeping command. An exact dispatch or server-side handler for `0x20800a26` was not identified in the published source searches. Its provider remains unknown at the available source boundary.

### Early GSP configuration exchange is different from the floorsweeping-mask request

[`kgspSendInitRpcs_IMPL` in `kernel_gsp.c` lines 6360–6400](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/src/kernel/gpu/gsp/kernel_gsp.c#L6360-L6400) calls `gmcapiCommand(..., GMCAPI_CMD_GSP_INIT, ...)`, receives key/value static data and decodes it. The [decoder at lines 9250–9367](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/src/kernel/gpu/gsp/kernel_gsp.c#L9250-L9367) handles, among other fields:

- `SKU_BOARD_ID`, `SKU_CONFIG_VERSION`, `CHIP_SKU`, internal client/device/subdevice handles;
- `ENGINE_MASK` (engine-type capabilities, **not** a demonstrated per-SM or TPC fuse map);
- various feature flags and PCI/VRAM metadata.

The inspected decoder does **not** establish raw GPC/TPC/SM fuse bitmaps or a resource-enabling override. `GMCAPI_CMD_GSP_INIT` is a separate initialization exchange from the later `NV2080_CTRL_CMD_INTERNAL_STATIC_KGR_GET_FLOORSWEEPING_MASKS` call; their content must not be equated.

### Genuine GB202 register-reading code, but for another purpose

[`kernel_gsp_gb202.c` lines 81–108](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/src/kernel/gpu/gsp/arch/blackwell/kernel_gsp_gb202.c#L81-L108) implements `kgspReadUcodeFuseVersion_GB202`. This calls `GPU_REG_RD32` at the GB202 GSP microcode-version fuse address (`NV_FUSE_ZB_OPT_FPF_GSP_UCODE1_VERSION`) and decodes the firmware-version fuse value. This is a **real fuse-related read** in public GB202 code, but is unrelated to SM/TPC/L2 resource disable masks and does not demonstrate user-mode access. The separate [`gpuIsInternalSkuFuseEnabled_GB202`](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/src/kernel/gpu/arch/blackwell/kern_gpu_gb202.c#L355-L373) only returns `NV_FALSE` without reading a fuse.

**Methodological correction:** the earlier nine-hit GB202 scan only covered `*blackwell/gb202/*` and `*kern_gpu_gb202.c` path globs, so it **did not cover** the file named `kernel_gsp_gb202.c` in `gsp/arch/blackwell/`. Nine is accurate for the chosen path filter, not a complete inventory of every GB202-related source file.

### Source-boundary assessment

| Claim | Evidence level | Interpretation |
|---|---|---|
| The generic internal RM call retrieves a per-engine floorsweeping structure | Confirmed from `kernel_graphics.c` | Value *consumer* proven |
| The GPU can route per-GPU RM control calls to GSP-RM on a GSP-client configuration | Confirmed from `rpc_common.c` and RPC declarations | General transport exists; specific command's full dispatch not traced |
| GSP supplies some SKU/engine configuration values during `GSP_INIT` | Confirmed from `kernel_gsp.c` | Not necessarily SM/TPC fuse masks |
| Public code can read one GB202 GSP microcode-version fuse | Confirmed from `kernel_gsp_gb202.c` | Not a compute-resource fuse |
| Effective SM/TPC disable masks are *assembled inside* GSP firmware | **Hypothesis; not directly shown** | May involve hardware fuses, firmware, security policy or combinations |
| Changing the returned mask structure changes actual functioning SM/TPC/L2 hardware | **Unsupported** | Caller-side output mutation is not proof of physical unit enablement |
| There is a reversible software-only RTX 5090 SM/L2 unlock | **Not demonstrated** | No suitable write/override path established |

The [NVIDIA README](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/README.md#L1-L21) says this is **Linux driver 620.70.06** and requires separate matching GSP firmware. This investigation does **not** claim the Windows 621.24 driver uses the identical call graph.

**Next technical decision:** Further source work should target the *provider* of the `0x20800a26` control and whether it reports immutable fuse-derived or computed effective topology. With the public provider still unidentified, the correct present conclusion is *unresolved provenance; no evidence of viable software-only override*, not a claim of impossibility or of a working bypass.
