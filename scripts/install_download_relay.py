#!/usr/bin/env python3
"""Install only the optional download relay; no audio decoder or Discord voice sender."""

import argparse
import ipaddress
import json
import os
import plistlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABEL = 'org.redaudioadapter.download-relay'


def private_write(path, value):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.fchmod(fd, 0o600)
    with os.fdopen(fd, 'w') as output:
        output.write(value)


def prepare(folder, env):
    required = ('GENE_RELAY_TOKEN', 'GENE_RELAY_BIND', 'GENE_RELAY_PEER')
    if not all(env.get(key) for key in required) or len(env['GENE_RELAY_TOKEN']) < 32:
        raise ValueError('Configure the private relay token and Tailscale peer/bind addresses')
    network = ipaddress.ip_network('100.64.0.0/10')
    if any(ipaddress.ip_address(env[key]) not in network for key in ('GENE_RELAY_BIND', 'GENE_RELAY_PEER')):
        raise ValueError('Relay bind and peer must be private overlay IPv4 addresses')
    deno = env.get('GENE_DENO_PATH') or shutil.which('deno')
    if not deno or not Path(deno).is_file() or not os.access(deno, os.X_OK):
        raise ValueError('Install Deno on PATH or set GENE_DENO_PATH to its executable')
    port = int(env.get('GENE_RELAY_PORT', '2335'))
    if not 1024 <= port <= 65535:
        raise ValueError('Choose an unprivileged relay port between 1024 and 65535')
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    (folder / 'red_audio_adapter').mkdir(exist_ok=True)
    (folder / 'red_audio_adapter/__init__.py').write_text('')
    for name in ('audio_resolver.py', 'audio_cache.py', 'audio_relay_server.py'):
        shutil.copyfile(ROOT / 'src/red_audio_adapter' / name, folder / 'red_audio_adapter' / name)
    shutil.copyfile(ROOT / 'scripts/run_audio_resolver.py', folder / 'run_audio_resolver.py')
    requirements = subprocess.check_output(['uv', 'export', '--frozen', '--no-dev', '--extra', 'audio',
                                            '--no-emit-project'], cwd=ROOT, text=True)
    (folder / 'requirements.txt').write_text(requirements)
    subprocess.run(['uv', 'venv', '--python', '3.11', str(folder / 'venv')], check=True)
    subprocess.run(['uv', 'pip', 'sync', '--require-hashes', '--python', str(folder / 'venv/bin/python'),
                    str(folder / 'requirements.txt')], check=True)
    values = {'GENE_RESOLVER_TOKEN': env['GENE_RELAY_TOKEN'], 'GENE_RELAY_ONLY': 'true',
              'GENE_RESOLVER_BIND': env['GENE_RELAY_BIND'], 'GENE_RELAY_PEER': env['GENE_RELAY_PEER'],
              'GENE_RESOLVER_PORT': env.get('GENE_RELAY_PORT', '2335'),
              'GENE_AUDIO_CACHE': str(folder / 'transfers'), 'GENE_DENO_PATH': str(Path(deno).resolve())}
    private_write(folder / 'resolver.env', ''.join(f'{key}={value}\n' for key, value in values.items()))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', type=Path)
    parser.add_argument('--release-sha')
    parser.add_argument('--env-file', type=Path, default=ROOT / '.env.local')
    parser.add_argument('--label', default=LABEL,
                        help='Use the existing service label when replacing an installed relay')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.-]{1,120}', args.label):
        parser.error('Use a plain reverse-domain service label')
    env = dict(line.split('=', 1) for line in args.env_file.read_text().splitlines()
               if '=' in line and not line.startswith('#'))
    if args.stage:
        prepare(args.stage.resolve(), env)
        print('Prepared the download-only relay. Running services are unchanged.')
        return
    if sys.platform != 'darwin':
        raise SystemExit('Service installation supports macOS; use --stage or the documented foreground command elsewhere')
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if args.release_sha != sha or not re.fullmatch('[a-f0-9]{40}', sha):
        raise SystemExit('--release-sha must match the complete HEAD commit')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise SystemExit('Commit changes before installing a release')
    folder = ROOT / '.audio/relay-releases' / sha
    if folder.exists():
        raise SystemExit('This relay release already exists; do not overwrite it')
    prepare(folder, env)
    plist = Path.home() / 'Library/LaunchAgents' / (args.label + '.plist')
    plist.parent.mkdir(parents=True, exist_ok=True)
    if plist.exists():
        shutil.copyfile(plist, folder / 'previous.plist')
    definition = {'Label': args.label, 'ProgramArguments': [str(folder / 'venv/bin/python'),
                  '-u', str(folder / 'run_audio_resolver.py')], 'WorkingDirectory': str(folder),
                  'RunAtLoad': True, 'KeepAlive': True, 'ProcessType': 'Background', 'Nice': 10,
                  'ThrottleInterval': 10, 'StandardOutPath': str(ROOT / '.audio/relay.log'),
                  'StandardErrorPath': str(ROOT / '.audio/relay.error.log')}
    plist.write_bytes(plistlib.dumps(definition))
    plist.chmod(0o600)
    subprocess.run(['launchctl', 'bootout', f'gui/{os.getuid()}', str(plist)], capture_output=True)
    subprocess.run(['launchctl', 'bootstrap', f'gui/{os.getuid()}', str(plist)], check=True)
    private_write(ROOT / '.audio/relay-release.json', json.dumps({'sha': sha, 'folder': str(folder), 'label': args.label}))
    print('Installed the download-only relay. Verify playback before retiring any previous release.')


if __name__ == '__main__':
    main()
