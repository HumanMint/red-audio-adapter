"""Build the external source and offline probes against pinned Lavalink libraries."""

import argparse
import hashlib
import os
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JAVA = Path(os.environ['JAVA_HOME']) / 'bin' if os.getenv('JAVA_HOME') else Path(shutil.which('javac') or 'javac').resolve().parent
URL = 'https://github.com/Cog-Creators/Lavalink-Jars/releases/download/3.7.13%2Bred.5/Lavalink.jar'
DIGEST = '64411785e471e926a2329af600563d6fc2a33428ab2c8f6705dab358460a9bbc'


def build(folder: Path, lavalink_jar: Path | None = None):
    folder.mkdir(parents=True, mode=0o700, exist_ok=True)
    jar = folder / 'Lavalink.jar'
    if lavalink_jar is not None and lavalink_jar.resolve() != jar.resolve():
        shutil.copyfile(lavalink_jar, jar)
    if not jar.exists():
        urllib.request.urlretrieve(URL, jar)
    if hashlib.sha256(jar.read_bytes()).hexdigest() != DIGEST:
        raise ValueError('Lavalink checksum does not match the pinned release')
    build_dir = folder / 'plugin-build'
    classes, libraries = build_dir / 'classes', build_dir / 'lib'
    classes.mkdir(parents=True, exist_ok=True)
    libraries.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(jar) as archive:
        for name in archive.namelist():
            if name.startswith('BOOT-INF/lib/') and name.endswith('.jar'):
                (libraries / Path(name).name).write_bytes(archive.read(name))
    subprocess.run([str(JAVA / 'javac'), '--release', '17', '-cp', str(libraries / '*'),
                    '-d', str(classes), *map(str, (ROOT / 'audio-plugin/src').rglob('*.java'))], check=True)
    metadata = classes / 'lavalink-plugins'
    metadata.mkdir(exist_ok=True)
    (metadata / 'gene-youtube.properties').write_text('path=gene.audio\nname=gene-youtube\nversion=0.2.0\n')
    output = folder / 'gene-youtube.jar'
    subprocess.run([str(JAVA / 'jar'), '--create', '--file', str(output), '-C', str(classes), '.'], check=True)
    probes = folder / 'probes'
    probes.mkdir(exist_ok=True)
    subprocess.run([str(JAVA / 'javac'), '--release', '17', '-cp', os.pathsep.join([str(libraries / '*'), str(classes)]),
                    '-d', str(probes), *map(str, (ROOT / 'audio-plugin/test').glob('*.java'))], check=True)
    # Keep the pinned libraries for the network-free UDP timing probe.
    shutil.copytree(libraries, folder / 'lib', dirs_exist_ok=True)
    shutil.rmtree(build_dir)
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / '.build')
    parser.add_argument('--lavalink-jar', type=Path, help='Use an existing pinned JAR; no download')
    args = parser.parse_args()
    print(build(args.output, args.lavalink_jar))
