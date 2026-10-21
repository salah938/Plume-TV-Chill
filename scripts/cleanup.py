#!/usr/bin/env python3
"""Remove this pack's cache; optionally remove only the explicitly requested old dev.plume."""
import argparse
import json
import shutil
import subprocess
import sys
from install import ROOT, LAUNCHER, Adb, verify_home


def main():
    parser = argparse.ArgumentParser(description='Nettoyage limite a ce pack et, sur demande, a ancien Plume.')
    parser.add_argument('--device')
    parser.add_argument('--apply', action='store_true', help='Appliquer ; sans cette option : apercu seulement')
    parser.add_argument('--remove-old-plume', action='store_true', help='Supprimer dev.plume et ses anciens reglages apres test de Home')
    args = parser.parse_args()
    plan = {'cache': str(ROOT / '.downloads'), 'uninstall': ['dev.plume'] if args.remove_old_plume else [],
            'amazon_packages_removed': [], 'apply': args.apply}
    print(json.dumps(plan, indent=2))
    if not args.apply:
        print('Aucune modification. Ajouter --apply pour executer ce plan.')
        return
    if args.remove_old_plume:
        adb = Adb(args.device)
        if not adb.installed(LAUNCHER):
            raise RuntimeError('Plume TV Chill doit etre installe avant le nettoyage.')
        verify_home(adb)
        if adb.installed('dev.plume'):
            print('Suppression de ancien dev.plume et de ses reglages. Les applications tierces sont conservees.')
            old = '/sdcard/Android/data/dev.plume/files/wallpapers'
            new = '/sdcard/Android/data/dev.plume.salah/files/wallpapers'
            try:
                adb.run('shell', 'test', '-d', old)
            except subprocess.CalledProcessError:
                pass
            else:
                adb.run('shell', 'mkdir', '-p', new)
                adb.run('shell', 'cp', '-Rn', old + '/.', new + '/')
            result = adb.run('uninstall', 'dev.plume')
            if 'Success' not in result or adb.installed('dev.plume'):
                raise RuntimeError('Desinstallation de ancien Plume non confirmee : ' + result)
        else:
            print('Ancien Plume deja absent.')
    shutil.rmtree(ROOT / '.downloads', ignore_errors=True)
    print('Nettoyage termine. Aucun composant Amazon supprime.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
