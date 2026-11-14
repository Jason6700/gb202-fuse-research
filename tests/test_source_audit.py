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


if __name__ == '__main__':
    unittest.main()
