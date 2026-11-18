# Review of the pinned source fuse/override scan — 2026-11-18

## Reproducible source

- Repository: [NVIDIA/open-gpu-kernel-modules](https://github.com/NVIDIA/open-gpu-kernel-modules)
- Pinned source commit: [`e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9`](https://github.com/NVIDIA/open-gpu-kernel-modules/tree/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9)
- User-observed previous scan: **145 matched source lines**, `may_be_truncated=false` using the original `--profile override`.
- **Important:** this original `override` mode also matches ordinary `FUSE_OPT` and `FUSE_STATUS` symbols. Its match count is **not** a count of usable software override paths.

## Interpretation by architecture

| Finding | Evidence | Scope |
|---|---|---|
| 106 lines from GA100 fuse header | [Ampere GA100 `dev_fuse.h`](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/common/inc/swref/published/ampere/ga100/dev_fuse.h) | Ampere, not RTX 5090 |
| 3 lines from GB100 fuse header | [Blackwell GB100 `dev_fuse_zb.h`](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/common/inc/swref/published/blackwell/gb100/dev_fuse_zb.h) | GB100, not GB202; includes security/firmware/display-related fuse symbols |
| 2 lines from GB100 kernel implementation | [`kern_gpu_gb100.c`](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/src/kernel/gpu/arch/blackwell/kern_gpu_gb100.c) | Not evidence of SM/L2 activation |
| 1 line from GB10B-specific source | [`kern_gpu_arch_gb10b.c`](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/src/kernel/gpu/arch/blackwell/kern_gpu_arch_gb10b.c) | Returns a GPC fuse-status register offset for GB10B, **not GB202** |
| **GB202 `dev_fuse_zb.h` exists but was missed by old profile** | [GB202-specific header](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/common/inc/swref/published/blackwell/gb202/dev_fuse_zb.h) | Contains `NV_FUSE_ZB_OPT_FPF_GSP_UCODE1_VERSION` and `NV_FUSE_ZB_OPT_FPF_SEC2_UCODE1_VERSION`; no SM/TPC/L2 disable/shadow definition in this **published header** |

The GB202 `dev_fuse_zb.h` file contains **only a limited subset** of fuse-related names. It is not a comprehensive register specification and must not be treated as evidence of which fuse controls exist in the silicon.

## Scanner refinement

The original `override` profile is retained for backwards compatibility. Two additional profiles make the evidence clearer:

- `fuse-register`: includes published `FUSE_ZB_OPT`, `FUSE_OPT`, `FUSE_STATUS` and fuse-related function symbols. A match proves **source text presence only**.
- `direct-override`: prioritizes explicit shadow/override control names. A match is a **candidate for manual investigation**, not proof of successful GB202 resource activation.

### Commands

Run from the parent `gb202-fuse-research` directory, after `git pull --ff-only`:

```powershell
python -m unittest discover -s tests -v

python tools/source_audit.py open-gpu-kernel-modules --profile fuse-register --path-glob "*blackwell/gb202/*" --path-glob "*kern_gpu_gb202.c" --max-matches 2000 --output reports/gb202-fuse-registers.json

python tools/source_audit.py open-gpu-kernel-modules --profile direct-override --max-matches 5000 --output reports/direct-override.json

$gb = Get-Content reports/gb202-fuse-registers.json -Raw | ConvertFrom-Json
$ov = Get-Content reports/direct-override.json -Raw | ConvertFrom-Json
$gb | Select-Object source_commit, scan_profile, match_count, may_be_truncated
$gb.matches | Select-Object -First 20 file, line, terms
$ov | Select-Object source_commit, scan_profile, match_count, may_be_truncated
$ov.matches | Group-Object file | Sort-Object Count -Descending | Select-Object -First 12 Count, Name
```

Both scans run only on locally cloned source text. The `direct-override` scan over the entire tree can still return non-GB202 symbols. Zero matches would not prove the absence of a silicon mechanism: published headers, secure firmware and actual hardware may differ.

## Open research questions

1. Find the provider of the privileged `NV2080_CTRL_CMD_INTERNAL_STATIC_KGR_GET_FLOORSWEEPING_MASKS` call, or explicitly document where the open driver ends and closed/secure firmware begins.
2. Find GB202-specific software-visible **effective** resource-mask initialization (not a generic fuse register, and not post-floorsweep logical topology).
3. Distinguish fused product policy, per-die defects, and post-fuse configuration. **The current data cannot decide why individual SM or L2 blocks are disabled.**
4. Keep the research read-only on the primary RTX 5090. No eFuse programming, voltage fault injection, MMIO writes, firmware patches, or experimental privileged driver loading.

**Conclusion:** no working reversible software-only GB202 SM/L2 unlock has been demonstrated by this scan.

## Follow-up results: GB202-only and whole-tree scans (2026-11-18)

**User-run result, pinned NVIDIA commit `e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9`:**

- `--profile fuse-register` restricted to `*blackwell/gb202/*` and `*kern_gpu_gb202.c`: **9 matches, untruncated**.
- `--profile direct-override` across the tree: **17 matches, untruncated**.

### GB202 nine-match breakdown

- **Eight lines:** [`gb202/dev_fuse_zb.h` lines 26–33](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/common/inc/swref/published/blackwell/gb202/dev_fuse_zb.h#L26-L33) consist of GSP and SEC2 microcode-version fuse register names and associated fields. These are not compute-resource disable masks.
- **One line:** [`kern_gpu_gb202.c` lines 355–373](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/src/kernel/gpu/arch/blackwell/kern_gpu_gb202.c#L355-L373) defines `gpuIsInternalSkuFuseEnabled_GB202`; despite the comment describing an internal SKU fuse, the **actual implementation simply returns `NV_FALSE` and performs no fuse read**.

### Complete classification of 17 direct-override-profile matches

| Count | Files/architecture | Actual matched constructs | GB202 SM/L2 enable evidence? |
|---:|---|---|---|
| 12 | `t234` (3), `gm107` (3), `gb100` (3), `ga100` (3) fuse headers | `FUSE_(ZB_)?STATUS_OPT_DISPLAY` status declarations and fields | **No**: display status, other architectures |
| 2 | [`kernel-open/nvidia/nv.c` lines 121 and 6756–6763](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/kernel-open/nvidia/nv.c#L6756-L6763) | `TEGRA264_STRAP_NV_FUSE_CTRL_OPT_GPU` and a Tegra `STRAP_SET` request | **No**: Tegra SoC strap handling, not GB202 graphics resource enabling. It *is* an example of a software write on another platform, not a GB202 override. |
| 1 | [`kern_gpu_gb100.c` line 1752](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/src/kernel/gpu/arch/blackwell/kern_gpu_gb100.c#L1743-L1754) | GB100 display-support fuse **read** | **No** |
| 2 | [`gb10b/dev_fuse.h` and `kern_gpu_arch_gb10b.c`](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/src/kernel/gpu/arch/blackwell/kern_gpu_arch_gb10b.c#L44-L48) | GB10B `NV_FUSE_STATUS_OPT_GPC` declaration / offset function | **No**: GPC **status offset** for another chip family, not a resource-enable operation |

The [generated GpuArch HAL table](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/generated/g_gpu_arch_nvoc.c#L207-L216) selects `gpuarchGetGpcFuseStatusOffset_GB10B` for **GB10B/GB10C** only, and [`osinit.c`](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/arch/nvalloc/unix/src/osinit.c#L1692-L1698) describes this offset as used by certain Tegra PCI integrated GPUs.

**Classification result:** **0 of the 17 inspected source matches demonstrates a GB202 SM/TPC/L2 override**, even though some match the scanner's lexical "direct-override" profile. This is a negative result *within the public source inspected*; it cannot prove the absence of all hidden firmware or silicon mechanisms.

### Provenance caveat and next research boundary

The pinned [NVIDIA source README](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/README.md#L1-L21) identifies this as **Linux open kernel-module version 620.70.06**, which requires separately supplied, version-matched GSP firmware and user-space components. The researcher's actual RTX 5090 runs **Windows driver 621.24**. Therefore, even confirmed behavior in this pinned Linux source does **not** by itself verify Windows driver internals.

A [source search for the static floorsweeping control](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/nvidia/src/kernel/gpu/gr/kernel_graphics.c#L1257-L1271) finds its public header declaration and the client-side `pRmApi->Control` invocation, not a verified public production GB202 provider of the response. Source inspection can locate the client/consumer boundary; it has not established whether the values originate in permanent eFuses, firmware-computed effective masks, or policy-based configuration.

**Next high-value action:** document the GSP/RM control-provider boundary rather than repeatedly scanning unqualified `FUSE_OPT` symbols; continue read-only investigation and seek source-level evidence specific to GB202 before proposing any runtime interaction.
