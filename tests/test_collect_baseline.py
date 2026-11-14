import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('collect_baseline', HERE / 'tools' / 'collect_baseline.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ParseTests(unittest.TestCase):
    def test_csv_parsing(self):
        line = 'NVIDIA GeForce RTX 5090, 621.14, 98.02.00.00.00, 32607, 0x2B85\n'
        parsed = mod.parse_query(line)
        self.assertEqual(parsed['name'], 'NVIDIA GeForce RTX 5090')
        self.assertEqual(parsed['memory.total'], '32607')
        self.assertEqual(len(parsed), len(mod.QUERY_FIELDS))

    def test_no_extra_records(self):
        with self.assertRaises(ValueError):
            mod.parse_query('bad,data\n')

    @patch.object(mod.subprocess, 'run')
    def test_read_only_command_and_no_uuid(self, run):
        run.return_value.stdout = 'RTX 5090, 621.14, 98.00, 32607, 0x2B85\n'
        result = mod.collect()
        argv = run.call_args.args[0]
        self.assertTrue(argv[0].endswith('nvidia-smi'))
        self.assertNotIn('uuid', ' '.join(argv).lower())
        self.assertNotIn('serial', ' '.join(argv).lower())
        self.assertEqual(result['cuda'], None)
        self.assertEqual(result['nvidia_smi']['driver_version'], '621.14')


if __name__ == '__main__':
    unittest.main()
