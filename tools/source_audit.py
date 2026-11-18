#!/usr/bin/env python3
"""Offline, read-only audit of public GPU driver source for topology keywords.

This indexes text references only. It does not access any device registers.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
from pathlib import Path
import re
import subprocess

BROAD_PATTERN = r'(?:floorsweep\w*|fuse\w*|gpc\w*|tpc\w*|ltc\w*|l2_?cache\w*|sm_to_gpc\w*|override\w*)'
FOCUSED_PATTERN = (
    r'(?:floorsweep\w*|phys_?gpc_?mask\w*|(?:gpc|tpc|ltc|l2)_?mask\w*|'
    r'sm_to_gpc_tpc_mappings|global_sm_order|fuse_(?:shadow|override|status|opt)\w*|'
    r'disable_sw_override|(?:ctrl|status)_opt_\w*)'
)
OVERRIDE_PATTERN = (
    r'(?:disable_sw_override|fuse_(?:shadow|override|status|opt)\w*|'
    r'ctrl_opt_\w*|status_opt_\w*|sw_?override\w*|shadow_?fuse\w*)'
)
PROFILES = {'broad': BROAD_PATTERN, 'focused': FOCUSED_PATTERN, 'override': OVERRIDE_PATTERN}
TERMS = ('floorsweep', 'fuse', 'gpc', 'tpc', 'ltc', 'l2cache', 'sm_to_gpc', 'override')
EXCLUDE = {'.git', '.venv', 'build', '__pycache__', 'node_modules'}
EXTS = {'.h', '.c', '.cc', '.cpp', '.py', '.md', '.txt'}
REGEX = re.compile(BROAD_PATTERN, re.IGNORECASE)


def audit(root: Path, max_matches: int = 500, *, profile: str = 'broad',
          path_globs: tuple[str, ...] = (), pattern: str | None = None) -> list[dict]:
    """Return up to max_matches matched source lines; preserve legacy API."""
    if profile not in PROFILES:
        raise ValueError(f'Unknown scan profile: {profile}')
    if max_matches < 1:
        raise ValueError('max_matches must be positive')
    matcher = re.compile(pattern or PROFILES[profile], re.IGNORECASE)
    matches = []
    for path in sorted(root.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in EXTS:
            continue
        rel = path.relative_to(root)
        if any(part in EXCLUDE for part in rel.parts):
            continue
        rel_name = rel.as_posix()
        if path_globs and not any(fnmatch.fnmatch(rel_name, glob) for glob in path_globs):
            continue
        try:
            if path.stat().st_size > 2_000_000:
                continue
            with path.open('r', encoding='utf-8', errors='replace') as stream:
                for number, line in enumerate(stream, start=1):
                    words = sorted({m.group(0).lower() for m in matcher.finditer(line)})
                    if words:
                        matches.append({'file': rel_name, 'line': number, 'terms': words})
                        if len(matches) >= max_matches:
                            return matches
        except OSError:
            continue
    return matches


def source_commit(root: Path) -> str | None:
    """Best-effort Git revision for reproducibility; no device information."""
    try:
        result = subprocess.run(
            ['git', '-C', str(root), 'rev-parse', 'HEAD'],
            check=True, text=True, capture_output=True, timeout=5,
        )
        commit = result.stdout.strip()
        return commit if re.fullmatch(r'[a-fA-F0-9]{40,64}', commit) else None
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_tree', type=Path, help='Locally checked-out public source tree')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--max-matches', type=int, default=500)
    parser.add_argument('--profile', choices=tuple(PROFILES), default='broad',
                        help='broad (legacy), focused (topology masks), or override')
    parser.add_argument('--path-glob', action='append', default=[],
                        help='Only include matching paths (repeatable), e.g. *ctrl2080internal.h')
    parser.add_argument('--regex', help='Custom case-insensitive regex, overrides profile regex')
    args = parser.parse_args()
    if not args.source_tree.is_dir() or args.max_matches < 1:
        parser.error('Provide an existing directory and a positive --max-matches')
    try:
        # Scan one extra match to distinguish actual truncation from an exact match count.
        found = audit(args.source_tree, args.max_matches + 1, profile=args.profile,
                      path_globs=tuple(args.path_glob), pattern=args.regex)
    except (ValueError, re.error) as exc:
        parser.error(str(exc))
    truncated = len(found) > args.max_matches
    matches = found[:args.max_matches]
    doc = {
        'schema_version': '2.0',
        'scan_root_name': args.source_tree.resolve().name,
        'source_commit': source_commit(args.source_tree),
        'scan_profile': args.profile if not args.regex else 'custom_regex',
        'regex': args.regex,
        'path_globs': args.path_glob,
        'limit': args.max_matches,
        'may_be_truncated': truncated,
        'match_count': len(matches),
        'matches': matches,
        'notes': 'Offline source-text index only; does not prove runtime register access, physical fuse values, or an unlock.',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(doc, indent=2) + '\n', encoding='utf-8')
    print(f'Indexed {len(matches)} lines ({"truncated" if truncated else "complete"}): {args.output}')


if __name__ == '__main__':
    main()
