#!/usr/bin/env python3
"""Find references to GPU floorsweeping and topology in a local source tree (offline)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

TERMS = ('floorsweep', 'fuse', 'gpc', 'tpc', 'ltc', 'l2cache', 'sm_to_gpc', 'override')
EXCLUDE = {'.git', '.venv', 'build', '__pycache__', 'node_modules'}
EXTS = {'.h', '.c', '.cc', '.cpp', '.py', '.md', '.txt'}
REGEX = re.compile(r'(?i)(?:floorsweep\w*|fuse\w*|gpc\w*|tpc\w*|ltc\w*|l2_?cache\w*|sm_to_gpc\w*|override\w*)')


def audit(root: Path, max_matches: int = 500) -> list[dict]:
    matches = []
    for path in sorted(root.rglob('*')):
        if len(matches) >= max_matches:
            break
        if not path.is_file() or path.suffix.lower() not in EXTS:
            continue
        if any(part in EXCLUDE for part in path.relative_to(root).parts):
            continue
        try:
            if path.stat().st_size > 2_000_000:
                continue
            with path.open('r', encoding='utf-8', errors='replace') as stream:
                for number, line in enumerate(stream, start=1):
                    words = sorted({m.group(0).lower() for m in REGEX.finditer(line)})
                    if words:
                        matches.append({
                            'file': path.relative_to(root).as_posix(),
                            'line': number,
                            'terms': words,
                        })
                        if len(matches) >= max_matches:
                            break
        except OSError:
            continue
    return matches


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_tree', type=Path, help='Locally checked-out, public source tree')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--max-matches', type=int, default=500)
    args = parser.parse_args()
    if not args.source_tree.is_dir() or args.max_matches < 1:
        parser.error('Provide an existing directory and a positive --max-matches')
    findings = audit(args.source_tree, args.max_matches)
    doc = {
        'scan_root_name': args.source_tree.resolve().name,
        'query_terms': TERMS,
        'limit': args.max_matches,
        'may_be_truncated': len(findings) == args.max_matches,
        'match_count': len(findings),
        'matches': findings,
        'notes': 'This index is an offline text search, not proof of register access or an unlock.',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(doc, indent=2) + '\n', encoding='utf-8')
    print(f'Indexed {len(findings)} line matches: {args.output}')


if __name__ == '__main__':
    main()
