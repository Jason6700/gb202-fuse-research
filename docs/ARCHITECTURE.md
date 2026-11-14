# Architecture and terminology

## GB202 baseline

The full GB202 design is described by NVIDIA as 12 GPCs, 96 TPCs, and 192 SMs. Retail GeForce RTX 5090 uses 170 SMs (21,760 CUDA cores). Published L2 configurations are 128 MB full design / 96 MB retail. See [SOURCES.md](SOURCES.md).

The difference between the configurations does **not** prove that an arbitrary retail GPU contains healthy, unlockable blocks.

## Levels of configuration evidence

1. **Physical silicon:** transistors and wires present in the die; cannot be validated by ordinary CUDA properties.
2. **Permanent fuse state:** one-time-programmable elements encoding configuration. A fuse is not necessarily a severed SM data path.
3. **Fuse-derived/effective masks:** configuration values applied during GPU initialization. There may be no writable software override in production GB202.
4. **Logical topology:** what the driver/runtime exposes *after floorsweeping*. IDs may be renumbered; missing logical IDs do not identify missing physical units.
5. **Functional validation:** tests that show new compute/cache is actually operating correctly, not merely advertised.

## Key API distinction

NVIDIA's public header `ctrl2080gr.h` defines control calls such as:

- `NV2080_CTRL_CMD_GR_GET_SM_TO_GPC_TPC_MAPPINGS`
- `NV2080_CTRL_CMD_GR_GET_GLOBAL_SM_ORDER`
- `NV2080_CTRL_CMD_GR_GET_PHYS_GPC_MASK`
- `NV2080_CTRL_CMD_GR_GET_NUM_TPCS_FOR_GPC`

Header presence does not guarantee these controls are callable from arbitrary Windows user-space processes or that they disclose immutable fuse values. The `GET_GLOBAL_SM_ORDER` description expressly refers to logical enabled IDs after floorsweeping.

## Critical unknowns

- Whether GB202 implements usable shadow/override values for SM, TPC, GPC, or L2 disabling.
- Whether these settings are latched before host software gains control.
- Whether GSP/firmware security and register privilege levels make them inaccessible.
- Whether disabled blocks are physically sound and validated at full operating conditions.
- Whether L2 disable masks are grouped with memory controllers and limited by other physical constraints.

Do **not** reuse GA100/Ada offsets on Blackwell without chip-specific evidence.
