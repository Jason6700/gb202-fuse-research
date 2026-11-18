# Preliminary NVIDIA topology interface catalog

**Status:** public-source inspection only. No GB202 register accesses, fuse reads, or unlocks have been demonstrated.

## Provenance

Reference checkout: NVIDIA [open-gpu-kernel-modules at e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9](https://github.com/NVIDIA/open-gpu-kernel-modules/tree/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9), the public main-branch commit examined on 2026-11-18. **The researcher's local NVIDIA checkout may be at a different commit.** Check with \`git -C open-gpu-kernel-modules rev-parse HEAD\` and cite that actual SHA for local scans.

This catalog records *declarations and comments in public headers*. They do not establish that a retail RTX 5090 running Windows can invoke any interface, that returned masks are physical eFuse values, or that a writable override exists.

## Relevant interfaces

| Symbol/field | Declared in the pinned source | What it supports | Critical limitation |
|---|---|---|---|
| \`NV2080_CTRL_CMD_GR_GET_SM_TO_GPC_TPC_MAPPINGS\` | [ctrl2080gr.h lines 763–787](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/common/sdk/nvidia/inc/ctrl/ctrl2080/ctrl2080gr.h#L763-L787) | An array of SM-to-GPC/TPC mappings | No explicit claim of raw factory fuse values |
| \`NV2080_CTRL_CMD_GR_GET_GLOBAL_SM_ORDER\` | [ctrl2080gr.h lines 1144–1214](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/common/sdk/nvidia/inc/ctrl/ctrl2080/ctrl2080gr.h#L1144-L1214) | Enabled SM/GPC/TPC **logical** ordering | Header explicitly says *post-floorsweeping*; IDs can be renumbered |
| \`NV2080_CTRL_CMD_GR_GET_GPC_MASK\` | [ctrl2080gr.h near line 1432](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/common/sdk/nvidia/inc/ctrl/ctrl2080/ctrl2080gr.h#L1418-L1442) | Declares a GPC-mask query | Mask origin, hardware mapping and GB202 access need verification |
| \`NV2080_CTRL_CMD_GR_GET_TPC_MASK\` | [ctrl2080gr.h lines 1450–1468](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/common/sdk/nvidia/inc/ctrl/ctrl2080/ctrl2080gr.h#L1450-L1468) | Enabled TPC mask for a specified GPC | Not an eFuse-read interface |
| \`NV2080_CTRL_CMD_GR_GET_PHYS_GPC_MASK\` | [ctrl2080gr.h near line 1764](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/common/sdk/nvidia/inc/ctrl/ctrl2080/ctrl2080gr.h#L1755-L1775) | A *physical GPC mask* query is declared | Physical mapping is not proof of raw fuse state or override |
| \`NV2080_CTRL_INTERNAL_STATIC_GR_FLOORSWEEPING_MASKS\` | [ctrl2080internal.h lines 311–348](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/common/sdk/nvidia/inc/ctrl/ctrl2080/ctrl2080internal.h#L311-L348) | Contains \`gpcMask\`, \`tpcMask[]\`, \`tpcCount[]\`, \`physGpcMask\`, \`physGfxGpcMask\` | Internal static interface; user-space availability and fuse provenance unknown |
| \`NV2080_CTRL_CMD_INTERNAL_STATIC_KGR_GET_FLOORSWEEPING_MASKS\` | [ctrl2080internal.h lines 350–363](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9/src/common/sdk/nvidia/inc/ctrl/ctrl2080/ctrl2080internal.h#L350-L363) | A static floorsweeping-mask control call is declared | Does not imply permission to call it on a GeForce device |

In the static floorsweeping structure, NVIDIA's comments specify that \`tpcMask[]\` is indexed by **logical GPC ID for MIG** and **physical GPC ID for non-MIG**, while \`tpcCount[]\` is always indexed by logical GPC ID. These semantics are crucial when comparing masks across devices.

## Evidence classification

- **Verified from public headers:** declarations and the stated logical/physical indexing semantics.
- **Unverified on GB202 retail:** whether a compatible read-only tool can access a relevant topology/mask interface on the researcher's Windows 11 RTX 5090.
- **Unknown:** permanent eFuse values, why each block was disabled, ability to change effective masks, health of disabled resources.
- **Not demonstrated:** reversible software-only SM or L2 activation.

## Reproduce a targeted source scan

Update the parent research repository and run:

\`\`\`powershell
git pull --ff-only
python -m unittest discover -s tests -v
git -C open-gpu-kernel-modules rev-parse HEAD
python tools/source_audit.py open-gpu-kernel-modules --profile focused --path-glob "*ctrl2080gr.h" --path-glob "*ctrl2080internal.h" --max-matches 5000 --output reports/topology-headers.json
$report = Get-Content reports/topology-headers.json -Raw | ConvertFrom-Json
$report | Select-Object source_commit, scan_profile, match_count, may_be_truncated
\`\`\`

For a wider search, omit \`--path-glob\` but retain \`--profile focused\`. The \`override\` profile scans for candidate source-code terms, but *even a matching symbol is not evidence of a usable GB202 override*. A negative scan cannot prove absence of hardware mechanisms.

## Next research tasks

1. Map which declarations are used in publicly available driver implementations, with source revision and call-site references.
2. Determine whether any read-only, documented interfaces are available on a retail Windows 11 RTX 5090; avoid arbitrary MMIO and privileged writes.
3. Keep physical/effective/fuse-derived classifications separate in the evidence log.
