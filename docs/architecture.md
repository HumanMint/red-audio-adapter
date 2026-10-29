# Architecture and protocol

Red's Audio cog uses an external Red-compatible Lavalink node. This project's Java
plugin implements its YouTube source through an authenticated resolver. The resolver
can extract/download directly on a suitably connected host or ask one trusted relay
to download a complete file. Lavalink decodes the locally cached file and sends voice.

The Python playback hook waits for `/prepare` before forwarding Red's selected track
to Lavalink. It wraps the pinned client's transport entry points; Red's queue,
commands and player implementation are unchanged. Stop, destroy and a newer play
supersede a pending preparation; pause/seek update its eventual transport settings.
Failures dispatch a valid `TRACK_EXCEPTION` to Red's ordinary notification/recovery path.
Install the hook once before commands run; it is not a dynamically reloadable cog.

## Network boundaries

- The Lavalink node is reachable only from Red's private container network.
- The resolver shares the node's private network namespace on port 2334. Its Java
  caller uses loopback; Red's separate container uses the node's private DNS alias.
  In this container layout it binds `0.0.0.0` inside that namespace, with no published
  host port. A same-host Python installation can instead bind loopback only.
- Lavalink uses its own password. The resolver and relay have separate bearer tokens,
  each at least 32 characters; tokens are never included in public configuration.
- The optional relay binds its configured overlay IPv4 address and permits the exact
  configured source peer. The resolver accepts relay URLs only in `100.64.0.0/10`;
  redirects, ambient proxies and forwarded-client-IP trust are disabled.
- An overlay address is not a credential. Network ACLs, source-peer validation and the
  token are separate required controls. No public HTTP ports are published by Compose.

## HTTP contract

All POST routes require `Authorization: Bearer <private-token>` and JSON
`{"identifier": "..."}`. `/health` is an unauthenticated private-network health read.

| Route | Service | Result |
| --- | --- | --- |
| `/load` | resolver or relay | Bounded YouTube metadata, search and playlist flags |
| `/prepare` | resolver | `{"ready": true}` only after a complete file is cached |
| `/resolve` | resolver | Local cache path and durable playback lease |
| `/release` | resolver | Release the supplied lease identifier |
| `/transfer` | relay | One complete bounded audio file with checksum/display metadata headers |

Transfers retain `X-Gene-Extension`, `X-Gene-SHA256` and base64 `X-Gene-Metadata`.
Refusals retain `X-Gene-Refusal` with only `too_long`, `too_large` or `unsupported`.
An upstream response body, signed media URL or extractor traceback is never relayed
as a member-facing explanation. The hook uses fixed text; unknown failures are generic.
These existing names and Java `gene.audio` / `gene-youtube` identifiers remain for compatibility.

## Storage and limits

Each track must be an ordinary public YouTube item, no more than 30 minutes and 64 MiB.
Playlist metadata is bounded to 100 entries; downloads are serialized and identical
cache misses coalesce. Cache publication requires a complete file and verified hash.

The service cache defaults to 256 MiB with a seven-day lifetime and a 2 GiB free-space
reserve. Choose an explicit budget for the host; no allocation percentage or current
machine size is assumed. Least-recently-used unleased files may be evicted at capacity.
Display metadata is bounded and excludes temporary stream URLs. Playback leases persist
in `.leases.json`, expire after two hours, and protect active files across resolver restarts.
A prepare handoff uses a shorter three-minute lease. Do not delete these files during migration.

The relay has temporary transfer files, not a persistent music library or Discord voice
connection. Completed/interrupted transfers are removed and its own abandoned transfer
directories are cleaned on restart. Its idle server waits for socket/signal events instead
of a periodic housekeeping loop. Cached files can play when the relay is unavailable;
uncached metadata and downloads still depend on it.
