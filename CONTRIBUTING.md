# Contributing

Contributions are welcome for **read-only telemetry**, public source analysis, architecture documentation, negative results, and evidence-backed hypotheses.

## Evidence standard

Every empirical finding should include GPU model and revision (if available), driver version, OS, method, tool source/commit, measurement, and limitations. Use the issue template. Do not publish unique hardware identifiers.

Every claim should use one of these tags:
- **Verified:** supported by an authoritative specification or independently reproduced evidence.
- **Observed:** directly measured; method and environment included.
- **Inferred:** logical interpretation of verified or observed facts.
- **Hypothesis:** unverified, testable mechanism.
- **Disproven:** falsified for a specified device and environment, not necessarily universally.

## Scope

Please submit read-only, reversible methods for the primary platform. Submit experimental approaches separately for discussion; do not package dangerous firmware or MMIO modifications as a default tool.

Run tests with `python -m unittest discover -s tests -v` before requesting review. Keep code and research records attributed to original authors.
