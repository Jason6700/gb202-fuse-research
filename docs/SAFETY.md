# Hardware and data safety policy

The RTX 5090 research card is a high-value daily-use GPU. The supported Phase 1 process is strictly **read-only**.

## Allowed in current phase

- Read GPU properties with documented CUDA runtime APIs.
- Run `nvidia-smi` property queries.
- Search public driver-source files offline.
- Analyze public documentation, published firmware metadata, and research papers offline.

## Out of scope

- Voltage fault injection, soldering, PCB modification, probe clips, or hardware programmers.
- Permanent fuse writes, strap modifications, power-limit bypass or custom voltage control.
- Arbitrary GPU MMIO writes, undocumented register writes or binary firmware patches on the primary card.
- Experimental kernel or boot drivers that modify GPU initialization on the primary card.

## Data privacy

Collectors omit serial number and GPU UUID. Logs should be checked for usernames, paths, UUIDs, serials and PCI bus topology before being published. Never commit complete proprietary firmware images or third-party copyrighted code without authorization.

## Failure policy

A denied query or missing driver property is an **unknown**, not proof of absent hardware. A crash is not evidence of functional unlock. Any future high-risk work must be documented separately and tested on expendable hardware.
