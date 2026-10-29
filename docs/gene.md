# Gene integration and migration

Gene depends on an exact source commit of the `red-audio-adapter` Python package.
Its startup still calls the preparation hook through `gene.runtime_audio`. The
legacy imports `gene.audio_cache`, `gene.audio_resolver`, `gene.audio_relay_server`
and `gene.runtime_audio` resolve to the new package, including existing monkeypatch
targets. Gene no longer owns the source plugin, resolver/cache implementation,
download relay, audio image builds or their tests.

Gene keeps its own Red cog/command diagnostics, trusted deployment authority,
`ops/audio-compose.yml` integration manifest and protected audio image references.
That manifest intentionally preserves existing mount paths, network alias and
service project; the portable adapter template is for a new installation.

## Updating the pair

1. Review and publish the adapter commit first. Update Gene's `ops/audio-adapter.json`
   with its exact full SHA, version and module hashes. Gene's image/development helper
   installs that verified bundle separately from its core dependency environment;
   its host controller services do not need the adapter. Keep the core lock and release
   dependency gate unchanged. Never track an adapter branch tip.
2. Run the adapter suite, Gene's full suite, lint and release-script mock tests. Check
   the installed wheel's compatibility imports. If Fri's compatibility suite depends
   on the changed paths, run it against the same Gene candidate.
3. Merge the adapter before Gene's integration. A production Gene runtime release
   installs the pinned package but does **not** build or replace the external audio
   node, resolver or relay. Follow the owner's maintenance window and merge/release bar.

## Independent audio rollout

Build external audio images from the adapter checkout, using the existing compatible
`gene-audio:<full-sha>` and `gene-audio-resolver:<full-sha>` tags. The tags now identify
adapter source commits for newly built images; old tags and source backups remain valid.
`GENE_AUDIO_SHA` pins the node and `GENE_AUDIO_RESOLVER_SHA` independently pins the resolver.
Keep the old node pin when only the resolver needs updating.

The Gene integration Compose file continues to consume those images and existing
private config/media mounts. Its separate `audio-release.env` remains the audio pin;
do not point the daily Gene/Fri batch at the new repo or retag active images implicitly.
Gene's retention tool continues to protect audio images; this extraction adds no cleanup.

For an installed relay, use the new repo's installer with its **existing label** and
private settings file. Keep the old release folder and saved service definition. A
new default label must not create a competing service or silently replace rollback assets.
Preserve media, metadata, leases, tokens and all Red/controller state in place.

## Mixed versions and rollback

This extraction preserves the current HTTP contract, fixed refusal codes, environment
names, Java source/plugin identity and member-facing text. Therefore a new Gene hook
can use existing node/resolver/relay services. Upgrading only the runtime may still show
the generic failure line when an older service cannot provide a specific refusal code.
That fallback does not confirm that the service upgrade or audio playback was verified.

Roll back a Gene source release through Gene's normal recovery. Roll back audio by
restoring its previous image pins/configuration and the previous relay service definition.
Do not restore stale controller state, clear the cache or delete private authentication
files to reverse this source ownership change. Actual audible playback remains an
operator test inside the authorized production maintenance window.
