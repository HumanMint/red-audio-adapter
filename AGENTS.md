# red-audio-adapter

Independent Red/Lavalink audio preparation, cache and optional private download relay.
Gene consumes a pinned Python package; this repo must not import Gene's controller,
read its database, own Discord requests, or gain deployment authority.

## Setup and validation

- Python 3.11, uv 0.11.30, JDK 21 for building the Java 17 plugin; Deno on downloader hosts.
- `uv sync --frozen --extra red --extra audio` installs test and downloader dependencies.
- `uv run --no-sync pytest -q` and `uv run --no-sync ruff check .`.
- `uv run --no-sync python scripts/build_audio_plugin.py` verifies the pinned Lavalink JAR
  before compiling. Use `--lavalink-jar <cached-public-jar>` for a network-free build.
- `docker build -f ops/Dockerfile.audio --target node -t gene-audio:check .` and
  `docker build -f ops/Dockerfile.audio --target resolver -t gene-audio-resolver:check .`.
- CI's UDP probe runs inside the node image with `--network none`; it proves local
  native sender timing, not Discord playback. See `docs/development.md`.

## Boundaries

- Existing `GENE_*` variables, `X-Gene-*` headers, Java source/plugin names and fixed
  refusal lines are compatibility interfaces. Keep them in this extraction.
- Keep resolver authentication, exact relay peer checks, private network restrictions,
  bounded transfers, checksums, free-space reserve, cache leases and cleanup semantics.
- Never accept arbitrary URLs, browser cookies, untrusted relays or public unauthenticated
  endpoints. Multi-user opt-in hosting is roadmap work, not an enabled feature.
- Use synthetic tracks and in-process HTTP transports in tests. Candidate/review tests
  run without credentials or outside network access. Never test through live member audio.
- Public docs, issues, reviews and CI output use generic installation examples and
  repository-relative links. Keep real host addresses, personal paths, account IDs,
  service topology, credentials and member content in private, ignored configuration.
- Preserve installed service labels and state during migration. No production action is
  authorized by this file. Coordinate production through the owner's Gene maintainer.
- Before shipping, obtain a fresh-context independent Sol review of the exact candidate.
  Coordinate shared review capacity with the owner; use one fresh reviewer per round.
- Credit substantive Codex-authored code/tests/docs with
  `Co-authored-by: Codex <noreply@openai.com>`, retaining human and other accurate authors.
  Record review-only help in the PR; never rewrite history solely for attribution.

## Layout

- `src/red_audio_adapter/`: resolver, cache, idle relay server and Red playback hook.
- `audio-plugin/`: external Lavalink source and native playback/timing probes.
- `scripts/`: reproducible plugin build and private relay staging/install tools.
- `ops/`: portable, private-network container configuration.
- `docs/`: setup, contract, migration, provenance and future relay hosting.
