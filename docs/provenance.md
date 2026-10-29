# Provenance

This project was extracted from [HumanMint/gene](https://github.com/HumanMint/gene)
at source commit `3a04670aa79aeb0b11a5d7202c519ba34106f9c3`.
The new repository starts with selected current source files, not a copy of Gene's
operational Git history or private configuration.

The selected-track recovery hook and its tests also incorporate Gene PR #96's
repair as merged at `532817d3a0ebe4c5027aff20c04020335ea5e5ce`, preserving Red's automatic
failure recovery without letting an older failure skip a newer play. The port changes
the Python namespace and test module expectations; Red's installed source is unchanged.
The merged hook and tests are byte-identical to the reviewed source at
`12b5b2225dd5869313b6e4d79a906d49354092fd` before that namespace adjustment.

| Gene source | New owner |
| --- | --- |
| `src/gene/audio_cache.py` | `src/red_audio_adapter/audio_cache.py` |
| `src/gene/audio_resolver.py` | `src/red_audio_adapter/audio_resolver.py` |
| `src/gene/audio_relay_server.py` | `src/red_audio_adapter/audio_relay_server.py` |
| `src/gene/runtime_audio.py` | `src/red_audio_adapter/runtime_audio.py` |
| `audio-plugin/` | `audio-plugin/` |
| `ops/Dockerfile.audio` | `ops/Dockerfile.audio` |
| `ops/audio-compose.yml` | Portable template in `ops/audio-compose.yml`; Gene keeps its deployment glue |
| `scripts/build_audio_plugin.py` | `scripts/build_audio_plugin.py` |
| `scripts/install_download_relay.py`, `run_audio_resolver.py` | Corresponding scripts, with portable setup |
| `tests/test_audio_*`, `tests/test_runtime_audio.py` | The four matching adapter test modules |

Gene's retired TCP proxy is not part of the current download-only architecture and
is not carried into this project. Gene's own audio command diagnostics stay with
its Red cog. Small compatibility modules remain in Gene for existing callers.

Public source paths are relative. No populated environment, installed identity,
cache, media file, personal host address, workstation path or service label is copied.

The adapter was developed for HumanMint's Gene project with assistance from Codex
and Claude. It builds against upstream Red, red-lavalink and Cog Creators' pinned
Lavalink distribution and uses Lavaplayer, yt-dlp, FastAPI, HTTPX and Uvicorn.
The selected Lavalink JAR is fetched from its upstream release and checked against
SHA-256 `64411785e471e926a2329af600563d6fc2a33428ab2c8f6705dab358460a9bbc`.
No upstream authors are represented as authors of these extraction commits.
