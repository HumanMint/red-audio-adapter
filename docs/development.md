# Development

```sh
uv sync --frozen --extra red --extra audio
uv run --no-sync pytest -q
uv run --no-sync ruff check .
uv build
```

Tests use synthetic video IDs, temporary media and in-process HTTP transports. The
Red tests exercise the installed Node/Player/dispatch and Red's notification/recovery
handler, not a live Discord connection. Run candidates and reviews with a clean
environment and network denied; setup may fetch public dependencies first.

Build the plugin and probes against the checksum-pinned upstream JAR:

```sh
uv run --no-sync python scripts/build_audio_plugin.py
# With the already-downloaded pinned public JAR, no network is needed:
uv run --no-sync python scripts/build_audio_plugin.py --lavalink-jar <cached-jar>
```

The plugin is `.build/gene-youtube.jar`; probes and pinned libraries are under
`.build/probes` and `.build/lib`. JDK 21 compiles Java 17 bytecode. CI builds the
node/resolver images and runs `UdpTimingProbe` in a container with no network except
its own loopback. The native sender probe uses loopback UDP and takes about 5 seconds.
It requires the native audio library to support the host architecture; the Linux image
is the reference environment for that check.

`PlaybackProbe` requires synthetic or operator-owned test audio plus a private local
resolver; it does not contact Discord. Do not run it against member content. A timing
probe, offline suite or successful image build does not establish audible playback.

When changing wire headers, Java plugin identifiers, cache/lease format, environment
names or the pinned Red/Lavalink versions, test old/new pairs before recommending a
rollout. Gene and the optional relay release independently from this repository.
