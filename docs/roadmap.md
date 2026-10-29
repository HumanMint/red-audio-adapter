# Opt-in relay hosting direction

The current release supports **one trusted operator-configured relay**. It has no
member enrollment, volunteer discovery, load balancing, hosted account service or
automatic failover. Do not expose it to arbitrary participants as though those
boundaries already exist.

A future version could let server members explicitly opt in to hosting a download
relay, with an easy installer and status/revoke controls. That work needs its own
protocol and privacy review before implementation:

- Consent and revocation: who authorizes a host, what it serves, and how to stop it.
- Separate credentials per host and caller, limited network reach, token rotation,
  health checks and a clear removal path without shared global credentials.
- Scheduling, capacity and failure handling that never trusts a volunteer's claimed
  file, metadata, checksum, path or error text as authority.
- A clear disclosure that the downloader sees requested video IDs and its outbound
  traffic uses its own connection. No collection of member conversations, browser
  sessions or Discord credentials on relay machines.
- Per-host resource/retention controls and supported OS packaging with straightforward
  uninstall and rollback.

Keep that capability in this repo. Gene may configure or consume an approved adapter,
but should not own its downloader, source plugin, relay accounts or hosting lifecycle.
