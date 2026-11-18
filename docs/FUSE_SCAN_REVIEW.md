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
