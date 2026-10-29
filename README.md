# red-audio-adapter

An independent audio adapter for [Red-DiscordBot](https://github.com/Cog-Creators/Red-DiscordBot).
It prepares complete public YouTube audio files before playback, serves them through
a Red-compatible Lavalink source, and can use one private download relay when the
bot host cannot download directly.

The relay downloads files; the bot host keeps the bounded cache and sends Discord
voice. Red retains its commands, queue, player and Audio cog. This project does not
patch the installed Red or red-lavalink source.

## Start here

- [Setup](docs/setup.md): prerequisites, private configuration, images and relay.
- [Architecture and protocol](docs/architecture.md): component boundaries and limits.
- [Gene integration](docs/gene.md): pinned dependency, deployment and rollback.
- [Development](docs/development.md): offline tests and Java checks.
- [Roadmap](docs/roadmap.md): future opt-in relay hosting.

This first release extracts the existing Gene adapter. The verified integration is
with Red **3.5.24**, red-lavalink **0.11.1**, and Cog Creators' Lavalink
**3.7.13+red.5**. It is not a general Lavalink 4 plugin or a one-click Red cog.
An embedding bot must install the playback-preparation hook before issuing audio
commands; Gene already does this. Standalone Red instructions explain that boundary.

## Supported today

- Public YouTube search, video and bounded playlist metadata.
- Complete, checksum-verified transfers; no partially downloaded track starts playing.
- A bounded cache, persistent playback leases, expiry and free-space reserve.
- One trusted private relay with a bearer token and exact source-peer restriction.
- Fixed refusal codes for tracks over 30 minutes, over 64 MiB, or unsupported sources.
- Stop, skip, pause and seek remain effective during preparation.

Private, sign-in-only, live and arbitrary URL downloads are not supported. No browser
cookies are collected. Multiple volunteer relays, automatic discovery, hosted accounts
and member opt-in are future work; this release does not accept untrusted relay hosts.

## Credits and license

[HumanMint](https://github.com/HumanMint) maintains the project. The adapter originated
in [Gene](https://github.com/HumanMint/gene); see [provenance](docs/provenance.md).
Early development used OpenAI Codex GPT-6 Astra and GPT-6.1 Sol; Codex and Claude
have contributed implementation, tests, integration and independent reviews.

Red-DiscordBot, Cog Creators, Red contributors, red-lavalink, Lavalink/Lavaplayer,
yt-dlp, FastAPI, HTTPX and Uvicorn provide the upstream foundations. This is an
independent community project, with no implied upstream endorsement.

Project code is [GPL-3.0-only](LICENSE). Dependencies retain their own licenses;
upstream code and binary notices must be retained when distributing images.
