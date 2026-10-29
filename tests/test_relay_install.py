"""Portable staging has its own package and never requires Gene or starts a service."""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('relay_install', ROOT / 'scripts/install_download_relay.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


def settings(tmp_path):
    deno = tmp_path / 'deno'
    deno.write_text('#!/bin/sh\nexit 0\n')
    deno.chmod(0o700)
    return {'GENE_RELAY_TOKEN': 'synthetic-relay-' + 'x' * 32,
            'GENE_RELAY_BIND': '100.64.0.1', 'GENE_RELAY_PEER': '100.64.0.2',
            'GENE_DENO_PATH': str(deno)}


def test_staged_release_is_self_contained_and_settings_are_private(tmp_path, monkeypatch):
    env = settings(tmp_path)
    folder = tmp_path / 'stage'
    monkeypatch.setattr(installer.subprocess, 'check_output', Mock(return_value='locked-dependencies\n'))
    run = Mock()
    monkeypatch.setattr(installer.subprocess, 'run', run)
    installer.prepare(folder, env)
    assert not (folder / 'gene').exists()
    assert (folder / 'red_audio_adapter/audio_resolver.py').is_file()
    assert "runpy.run_module('red_audio_adapter.audio_resolver'" in (folder / 'run_audio_resolver.py').read_text()
    values = dict(line.split('=', 1) for line in (folder / 'resolver.env').read_text().splitlines())
    assert values['GENE_RESOLVER_TOKEN'] == env['GENE_RELAY_TOKEN']
    assert values['GENE_RELAY_ONLY'] == 'true'
    assert values['GENE_DENO_PATH'] == env['GENE_DENO_PATH']
    assert (folder / 'resolver.env').stat().st_mode & 0o777 == 0o600
    assert all(call.args[0][0] == 'uv' for call in run.call_args_list)
    # Import from the staged package with the project's normal path removed.
    # Restore the real subprocess runner before the import probe.
    monkeypatch.undo()
    result = subprocess.run([sys.executable, '-c',
        'import red_audio_adapter.audio_resolver; import sys; assert "gene" not in sys.modules'],
        cwd=folder, env={**os.environ, 'PYTHONPATH': str(folder)}, capture_output=True)
    assert result.returncode == 0, result.stderr.decode()


@pytest.mark.parametrize('change', [
    {'GENE_RELAY_BIND': '0.0.0.0'}, {'GENE_RELAY_PEER': '203.0.113.10'},
    {'GENE_RELAY_PORT': '80'}, {'GENE_RELAY_TOKEN': 'short'}, {'GENE_DENO_PATH': '/missing/deno'},
])
def test_invalid_installation_is_refused_before_creating_files(tmp_path, change):
    env = settings(tmp_path) | change
    with pytest.raises(ValueError):
        installer.prepare(tmp_path / 'stage', env)
    assert not (tmp_path / 'stage').exists()
