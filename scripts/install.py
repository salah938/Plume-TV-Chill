#!/usr/bin/env python3
"""Install the verified Fire TV bundle. Python 3.9+, adb; no Python dependencies."""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = 'dev.plume.salah'  # Stable update identity; the visible name is Plume TV Chill.
COMPONENT = LAUNCHER + '/dev.plume.MainActivity'
HOF = 'io.github.toolicious.homeonfire'


def verify_digest(path, expected):
    digest = hashlib.sha256()
    with Path(path).open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    if digest.hexdigest() != expected:
        raise ValueError('Empreinte SHA-256 incorrecte : ' + str(path))


def validate_apps(apps):
    ids = set()
    for app in apps:
        if app['id'] in ids or not re.fullmatch(r'[a-z0-9-]+', app['id']):
            raise ValueError('Identifiant duplique ou invalide')
        ids.add(app['id'])
        if not re.fullmatch(r'[0-9a-f]{64}', app['sha256']):
            raise ValueError('Empreinte SHA-256 requise')
        if bool(app.get('url')) == bool(app.get('file')):
            raise ValueError('Une seule source par application')
        if app.get('url') and not app['url'].startswith('https://'):
            raise ValueError('HTTPS requis')
        if app.get('file') and (ROOT not in (ROOT / app['file']).resolve().parents):
            raise ValueError('Fichier hors du depot')


class HTTPSRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not newurl.startswith('https://'):
            raise ValueError('Redirection de telechargement non HTTPS refusee')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(app):
    if 'file' in app:
        path = ROOT / app['file']
        verify_digest(path, app['sha256'])
        return path
    cache = ROOT / '.downloads'
    cache.mkdir(exist_ok=True)
    path = cache / (app['id'] + '.apk')
    if path.exists():
        try:
            verify_digest(path, app['sha256'])
            return path
        except ValueError:
            pass
    print('Telechargement : ' + app['name'], flush=True)
    opener = urllib.request.build_opener(HTTPSRedirect())
    request = urllib.request.Request(app['url'], headers={'User-Agent': 'Plume-TV-Chill-Installer/1.0'})
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=cache, suffix='.part', delete=False) as output:
            temporary = Path(output.name)
            with opener.open(request, timeout=90) as response:
                count = 0
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    count += len(chunk)
                    if count > 512 * 1024 * 1024:
                        raise ValueError('Telechargement trop volumineux')
                    output.write(chunk)
        verify_digest(temporary, app['sha256'])
        os.replace(temporary, path)
        return path
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


class Adb:
    def __init__(self, device=None):
        binary = shutil.which('adb')
        if not binary:
            raise RuntimeError('ADB absent. Voir README : installer Android Platform Tools.')
        self.base = [binary]
        if device:
            if device.startswith('-') or not re.fullmatch(r'[A-Za-z0-9_.:\[\]-]+', device):
                raise ValueError('Adresse ou numero ADB invalide')
            if ':' in device or re.fullmatch(r'\d+\.\d+\.\d+\.\d+', device):
                device = device if ':' in device else device + ':5555'
                subprocess.run([binary, 'connect', device], check=True, timeout=30)
            self.base += ['-s', device]
        self.run('get-state')

    def run(self, *args, timeout=90):
        result = subprocess.run(self.base + list(args), check=True, capture_output=True,
                                text=True, encoding='utf-8', errors='replace', timeout=timeout)
        return result.stdout.strip()

    def installed(self, package):
        return self.run('shell', 'pm', 'path', package).startswith('package:')

    def resumed(self):
        return '\n'.join(line for line in self.run('shell', 'dumpsys', 'activity', 'activities').splitlines()
                         if 'mResumedActivity' in line or 'topResumedActivity' in line)


def verify_home(adb):
    adb.run('shell', 'am', 'start', '-W', '-a', 'android.settings.SETTINGS')
    adb.run('shell', 'input', 'keyevent', 'KEYCODE_HOME')
    start = time.monotonic()
    while time.monotonic() - start < 15:
        if LAUNCHER + '/' in adb.resumed():
            return round(time.monotonic() - start, 2)
        time.sleep(.4)
    raise RuntimeError('Le bouton Home ne revient pas a Plume TV Chill. Voir .logs et Home on Fire.')


def main(argv=None):
    parser = argparse.ArgumentParser(description='Installer Plume TV Chill et ses applications sur un Fire TV.')
    parser.add_argument('--device', help='IP du Stick ou numero ADB ; obligatoire si plusieurs appareils')
    parser.add_argument('--dry-run', action='store_true', help='Afficher le plan sans telecharger ni modifier le Stick')
    parser.add_argument('--download-only', action='store_true', help='Telecharger et verifier les APK sans ADB')
    parser.add_argument('--apps', nargs='+', choices=['plume', 'smarttube', 'zen', 'home-on-fire'],
                        default=['plume', 'smarttube', 'zen', 'home-on-fire'])
    parser.add_argument('--update-existing', action='store_true', help='Mettre aussi a jour les applications tierces deja installees')
    parser.add_argument('--skip-home', action='store_true', help='Ne pas configurer la redirection Home')
    parser.add_argument('--apk', type=Path, action='append', default=[], help='APK local supplementaire fourni par son utilisateur')
    parser.add_argument('--clean-downloads', action='store_true', help='Effacer seulement le cache de ce pack apres reussite')
    args = parser.parse_args(argv)
    apps = json.loads((ROOT / 'apps.lock.json').read_text(encoding='utf-8'))['apps']
    validate_apps(apps)
    selected = [app for app in apps if app['id'] in args.apps]
    for path in args.apk:
        if not path.is_file() or path.suffix.lower() != '.apk':
            parser.error('APK local introuvable : ' + str(path))
    if args.dry_run:
        print(json.dumps({'applications': selected, 'configure_home': not args.skip_home,
                          'extra_apks': [str(p) for p in args.apk], 'device_modified': False}, ensure_ascii=False, indent=2))
        return 0
    adb = None if args.download_only else Adb(args.device)
    if adb:
        api = int(adb.run('shell', 'getprop', 'ro.build.version.sdk'))
        abis = adb.run('shell', 'getprop', 'ro.product.cpu.abilist')
        if api < 26 or 'armeabi-v7a' not in abis:
            raise RuntimeError('Ce pack cible Android API 26+ avec compatibilite ARM 32 bits (armeabi-v7a).')
    report = {'applications': [], 'home_verified': False}
    logs = ROOT / '.logs'
    logs.mkdir(exist_ok=True)
    try:
        for app in selected:
            existing = adb and adb.installed(app['package'])
            if existing and app['id'] != 'plume' and not args.update_existing:
                print('Conservee, deja installee : ' + app['name'], flush=True)
                report['applications'].append({'id': app['id'], 'status': 'already-installed'})
                continue
            path = fetch(app)
            if adb:
                print('Installation : ' + app['name'], flush=True)
                result = adb.run('install', '-r', str(path), timeout=300)
                if 'Success' not in result or not adb.installed(app['package']):
                    raise RuntimeError('Installation non confirmee : ' + app['name'] + '\n' + result)
            report['applications'].append({'id': app['id'], 'status': 'installed' if adb else 'downloaded'})
        if adb:
            for path in args.apk:
                result = adb.run('install', '-r', str(path.resolve()), timeout=300)
                if 'Success' not in result:
                    raise RuntimeError('Installation non confirmee : ' + str(path))
            if not args.skip_home:
                if not adb.installed(LAUNCHER) or not adb.installed(HOF):
                    raise RuntimeError('Plume TV Chill et Home on Fire doivent etre installes pour configurer Home.')
                from home_setup import configure
                configure(adb, logs)
                report['home_return_seconds'] = verify_home(adb)
                report['home_verified'] = True
            adb.run('shell', 'am', 'start', '-W', '-n', COMPONENT)
        if args.clean_downloads:
            shutil.rmtree(ROOT / '.downloads', ignore_errors=True)
        print('Termine. Voir .logs/install-report.json. Aucun compte ni abonnement configure.', flush=True)
        return 0
    finally:
        (logs / 'install-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print('Installation interrompue : ' + str(error), file=sys.stderr)
        sys.exit(1)
