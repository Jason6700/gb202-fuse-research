import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('source_audit', HERE / 'tools' / 'source_audit.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class SourceAuditTests(unittest.TestCase):
    def test_findings(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / 'gpu.h'
            path.write_text('GPC topology\nNV2080_CTRL_FUSE_OVERRIDE\nno match\n')
            found = mod.audit(Path(tmp))
            self.assertEqual(len(found), 2)
            self.assertEqual(found[0]['line'], 1)
            self.assertEqual(found[1]['file'], 'gpu.h')

    def test_skips_git(self):
        with TemporaryDirectory() as tmp:
            hidden = Path(tmp) / '.git'
            hidden.mkdir()
            (hidden / 'x.txt').write_text('fuse')
            self.assertEqual(mod.audit(Path(tmp)), [])

    def test_focused_profile_ignores_generic_gpc(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / 'ctrl2080internal.h'
            path.write_text('GPC topology\nNvU32 physGpcMask;\nNvU32 tpcMask[32];\n')
            found = mod.audit(Path(tmp), profile='focused')
            self.assertEqual(len(found), 2)
            self.assertEqual([x['line'] for x in found], [2, 3])

    def test_path_glob_filter(self):
        with TemporaryDirectory() as tmp:
            (Path(tmp) / 'one.h').write_text('floorsweepingMasks\n')
            (Path(tmp) / 'two.h').write_text('floorsweepingMasks\n')
            found = mod.audit(Path(tmp), profile='focused', path_globs=('*two.h',))
            self.assertEqual([x['file'] for x in found], ['two.h'])

    def test_override_profile_excludes_general_fuse(self):
        with TemporaryDirectory() as tmp:
            (Path(tmp) / 'gpu.h').write_text('fuse count\nCTRL_OPT_FUSE_ID\nDISABLE_SW_OVERRIDE\n')
            found = mod.audit(Path(tmp), profile='override')
            self.assertEqual(len(found), 2)
            self.assertEqual([x['line'] for x in found], [2, 3])


if __name__ == '__main__':
    unittest.main()
