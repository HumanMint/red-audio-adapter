# Setup

Use a private test installation first. This project supplies the audio services and
playback hook, not a Discord bot token, Red installation or public hosting service.
The tested combination is Red 3.5.24, red-lavalink 0.11.1 and Lavalink 3.7.13+red.5.
Keep a working previous node, resolver, relay and configuration available for rollback.

## 1. Install the source and tools

```sh
git clone https://github.com/HumanMint/red-audio-adapter.git
cd red-audio-adapter
uv sync --frozen --extra red --extra audio
```

Use Python 3.11 and uv 0.11.30. Java builds need JDK 21 (`JAVA_HOME` or `javac` on PATH).
Container builds need Docker/Compose. Downloader hosts also need Deno on PATH or a
private `GENE_DENO_PATH` pointing to its executable. The downloader uses pinned yt-dlp
with no personal cookies. Network access may still be refused by the source; this
adapter does not guarantee that every connection can retrieve every public track.

## 2. Configure the private audio host

Choose private absolute configuration/media directories and a private Docker network
shared with Red. Create the directories for UID/GID 10001; make configuration files
readable by that UID only. Do not copy populated configuration into the source tree.
Use the three examples under `ops/`:

- `application.yml.example` becomes `application.yml` in your private config directory.
  Replace the Lavalink password and resolver-token placeholders with different private
  credentials. Keep native YouTube, arbitrary HTTP and local sources disabled: the
  external plugin internally loads only files validated by the resolver/cache.
- `resolver.env.example` becomes `resolver.env` beside it. Use the same resolver token
  as the plugin and a separate relay token. Supply your private relay URL and explicitly
  choose cache bytes, TTL and free-space reserve. Never commit the result.
- `release.env.example` becomes a private Compose environment file. Fill its directories,
  Docker network and full immutable source/image SHAs. An existing deployment may keep
  its current node pin while updating only the resolver.

Generate each credential locally, for example with `python3 -c 'import secrets;
print(secrets.token_urlsafe(48))'`, and store it directly in your private configuration.
Do not paste tokens into issues, chat, shell arguments or CI logs. The default Compose
template publishes no host ports. The Red container must join the configured private
network; the node's compatibility DNS alias is `gene-audio`.

Build both images **from this checkout**, replacing `<adapter-sha>` with its full
`git rev-parse HEAD`. Put that tag in the private release file:

```sh
docker build -f ops/Dockerfile.audio --target node -t gene-audio:<adapter-sha> .
docker build -f ops/Dockerfile.audio --target resolver -t gene-audio-resolver:<adapter-sha> .
docker compose --env-file <private-release-file> -f ops/audio-compose.yml config --quiet
docker compose --env-file <private-release-file> -f ops/audio-compose.yml up -d
```

The supplied Docker resolver uses a relay. Direct downloading is available through
the Python service on a host with the `audio` extra and Deno installed; the Docker
resolver intentionally contains neither the downloader extra nor a JavaScript runtime.
For direct mode, omit `GENE_RELAY_URL` and configure a private writable cache directory
before running `uv run --no-sync red-audio-resolver`. Keep it loopback-only beside its
Lavalink node, with the same cache path visible to the plugin.

## 3. Optional private download relay

On a trusted downloader machine, install this repo, uv, Python 3.11 and Deno. Copy
`.env.example` to ignored `.env.local` with mode 0600 and configure:

| Value | Meaning |
| --- | --- |
| `GENE_RELAY_TOKEN` | Separate relay token, at least 32 characters |
| `GENE_RELAY_BIND` | This machine's private overlay IPv4 address |
| `GENE_RELAY_PEER` | Exact private overlay IPv4 source allowed to call it |
| `GENE_RELAY_PORT` | Unprivileged port; default 2335 |
| `GENE_DENO_PATH` | Optional absolute executable path, resolved from PATH if omitted |

Do not expose this port publicly. Configure overlay ACLs for the intended host/port.
Staging creates an isolated release and does not start or stop a service:

```sh
uv run --no-sync python scripts/install_download_relay.py --stage .audio/relay-stage
```

You can run the staged relay in the foreground on Linux or macOS:

```sh
.audio/relay-stage/venv/bin/python .audio/relay-stage/run_audio_resolver.py
```

On macOS, install a committed immutable release as a user LaunchAgent:

```sh
uv run --no-sync python scripts/install_download_relay.py --release-sha <adapter-sha>
```

The default label is `org.redaudioadapter.download-relay`. **When replacing an existing
relay, pass `--label <existing-label>`** so the installer replaces that service rather
than starting a second one. Retain the former release and saved plist for rollback.
Use `--env-file <private-file>` if settings live elsewhere. Automatic Linux/Windows
service installation is not implemented; foreground execution is the current option.

## 4. Connect Red and install the preparation hook

Configure Red's external Lavalink connection to the private node at port 2333 with
the private Lavalink password, using the settings supported by the pinned Audio cog.
Do not expose Lavalink or the resolver on a public interface. Gene's runtime already
sets the external-node configuration; see [Gene integration](gene.md).

The embedding runtime must call the following once during startup, before music
commands can run:

```python
from red_audio_adapter.runtime_audio import install_audio_preparation
install_audio_preparation(bot)
```

Set `GENE_AUDIO_PREPARE_URL=http://gene-audio:2334` (or loopback for a same-host process),
`GENE_AUDIO_PREPARE_TOKEN` to the resolver token, and `GENE_GUILD_ID` to the opted-in
server. This first version supports one configured server for the hook. Other servers
keep their normal transport. The hook has no effect unless its URL is configured.
Stock Red does not load this hook merely because the package is installed; a supported
startup integration is required. An easy installable cog is future packaging work.

## 5. Verify and recover

Run offline tests and native probes before a switch. On your private test server,
verify search, a cold preparation, audible playback, cached replay with the relay
unavailable, stop/skip during preparation, pause/seek, a refusal and the next track.
A health read, a successful search or an accepted play operation does not prove audio.

If the candidate fails, restore the previous image pins, configuration and relay plist.
Keep current cache metadata/leases and private identities; do not reset Red's queue,
library, credentials or controller state. Retire only the explicitly replaced service
after the replacement passes. Never use a broad Docker prune as part of this setup.
