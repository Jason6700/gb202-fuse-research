#!/usr/bin/env python3
"""Collect a minimal, read-only NVIDIA GPU baseline (no UUID/serial queries)."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

# Driver-supported names; errors are reported rather than bypassed.
QUERY_FIELDS = (
    'name', 'driver_version', 'vbios_version', 'memory.total', 'pci.device_id'
)


def parse_query(stdout: str, fields=QUERY_FIELDS) -> dict[str, str]:
    """Parse exactly one row from nvidia-smi's no-header CSV mode."""
    rows = list(csv.reader(stdout.splitlines(), skipinitialspace=True))
    if len(rows) != 1 or len(rows[0]) != len(fields):
        raise ValueError(f'Expected 1 CSV row with {len(fields)} fields, got {rows!r}')
    return dict(zip(fields, [value.strip() for value in rows[0]]))


def collect(gpu_index: int = 0, cuda_probe: str | None = None) -> dict:
    cmd = [
        'nvidia-smi', f'--id={gpu_index}',
        '--query-gpu=' + ','.join(QUERY_FIELDS),
        '--format=csv,noheader,nounits',
    ]
    try:
        result = subprocess.run(cmd, text=True, capture_output=True, check=True, timeout=15)
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError('nvidia-smi did not complete; check driver and query availability') from exc
    record = {
        'schema_version': '1.0',
        'captured_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'gpu_index': gpu_index,
        'nvidia_smi': parse_query(result.stdout),
        'cuda': None,
        'notes': 'Read-only advertised properties. Neither fuse values nor physical health measured.',
    }
    if cuda_probe:
        try:
            cuda = subprocess.run(
                [cuda_probe, str(gpu_index)], text=True, capture_output=True,
                check=True, timeout=30,
            )
            values = json.loads(cuda.stdout)
        except (OSError, ValueError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            raise RuntimeError('Optional CUDA probe failed or returned invalid JSON') from exc
        if not isinstance(values, dict) or not {'sm_count', 'l2_bytes'} <= values.keys():
            raise RuntimeError('CUDA probe did not return required properties')
        record['cuda'] = values
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gpu-index', type=int, default=0, help='GPU index (default: 0)')
    parser.add_argument('--cuda-probe', help='Optional path to locally compiled cuda_probe executable')
    parser.add_argument('--output', type=Path, required=True, help='JSON destination')
    args = parser.parse_args()
    if args.gpu_index < 0:
        parser.error('--gpu-index must be non-negative')
    try:
        record = collect(args.gpu_index, args.cuda_probe)
    except (RuntimeError, ValueError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f'Wrote read-only baseline to {args.output}')
    print('Review report for personal information before publishing.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
