"""Synthetic Red configuration; never use an installed bot's private settings."""

import os
from tempfile import TemporaryDirectory

_red_config = TemporaryDirectory(prefix='red-audio-test-config-')
os.environ['XDG_CONFIG_HOME'] = _red_config.name
