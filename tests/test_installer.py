import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('installer', ROOT / 'scripts/install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)

class InstallerTest(unittest.TestCase):
    def test_checksum_rejects_corrupt_download(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'app.apk'
            path.write_bytes(b'original signed APK')
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            installer.verify_digest(path, digest)
            path.write_bytes(b'corrupted')
            with self.assertRaisesRegex(ValueError, 'Empreinte'):
                installer.verify_digest(path, digest)

    def test_manifest_requires_https_unique_ids_and_known_hashes(self):
        good = {'id': 'zen', 'name': 'Zen', 'package': 'app.zeniptv.mobile', 'url': 'https://zeniptv.app/app.apk', 'sha256': 'a' * 64}
        installer.validate_apps([good])
        with self.assertRaises(ValueError):
            installer.validate_apps([good, good])
        with self.assertRaises(ValueError):
            installer.validate_apps([{**good, 'url': 'http://example.com/app.apk'}])
        with self.assertRaises(ValueError):
            installer.validate_apps([{**good, 'sha256': ''}])
        with self.assertRaises(ValueError):
            installer.validate_apps([{**good, 'file': '../private.apk'}])

    def test_plan_includes_both_requested_players_and_no_private_apks(self):
        manifest = json.loads((ROOT / 'apps.lock.json').read_text())
        installer.validate_apps(manifest['apps'])
        self.assertEqual({'plume', 'smarttube', 'zen', 'home-on-fire'}, {a['id'] for a in manifest['apps']})
        zen = next(a for a in manifest['apps'] if a['id'] == 'zen')
        self.assertEqual('https://zeniptv.app/releases/zeniptv_fireos.apk', zen['url'])
        smart = next(a for a in manifest['apps'] if a['id'] == 'smarttube')
        self.assertIn('armeabi-v7a', smart['url'])
        self.assertEqual(['plume'], [a['id'] for a in manifest['apps'] if 'file' in a])

if __name__ == '__main__':
    unittest.main()
