# AI / automation contributor instructions

Research objective: evidence-based feasibility study for software-only, reversible GB202 SM/L2 activation.

- Do not claim a confirmed unlock without independent validation on GB202.
- Treat GA100/Ada register names, offsets and implementation details as architecture-specific; never present them as confirmed GB202 values.
- Never write code that writes eFuses, manipulates power/voltage, flashes firmware, loads custom privileged drivers, or writes arbitrary MMIO on the user's primary GPU.
- Label sourced claims with links, revision/date, and observed vs inferred status.
- Keep measurement tools read-only. Do not collect GPU UUID, serial numbers, user paths, or personal identifiers by default.
- A changed SM count or L2 reporting value alone is not proof of working hardware. Require independent functional and repeatability evidence in a controlled environment.
- Prefer Python standard library; keep collectors cross-checkable, small, and auditable.
