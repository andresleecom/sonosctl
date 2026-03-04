# Sonos CLI Context Log

Last updated: 2026-03-04

## Goal
Build and validate a local CLI tool to control Sonos speakers and Spotify playback on the same LAN.

## Current Status
- Sonos discovery works.
- Spotify search/play works after completing SoCo auth flow.
- Multi-speaker discovery confirmed:
  - `Coffee Room` (`192.168.68.110`)
  - `Dining Room` (`192.168.68.106`)

## Architecture
- Language: Python
- Core library: `soco`
- Entry point: `sonos_spotify_cli.py`
- Package config: `pyproject.toml`
- User docs: `README.md`

## Commands Implemented
- `devices`
- `search`
- `play`
- `pause`
- `resume`
- `next`
- `prev`
- `volume`
- `auth-spotify`

## Features Implemented
- JSON output:
  - `devices --json`
  - `search --json`
- Interactive pick:
  - `play --pick`
- Config defaults in `~/.sonosctl/config.toml`
- Speaker-scoped Spotify service usage for `search`/`play`

## Auth/Token Issue History
- Observed error:
  - `Authorization for Spotify expired, is invalid or has not yet been completed: [ns0:Client.AuthTokenExpired / authTokenExpired / None]`
- Root cause:
  - Sonos-side/SoCo token flow required dedicated SoCo auth.
- Fix added:
  - `auth-spotify` command to run SoCo device link flow.

## SoCo Auth Command Behavior (Important)
`begin_authentication()` returned different shapes depending on environment:
- tuple/list
- dict
- URL string only

CLI now supports all three and extracts `linkCode` from URL query when needed.

## Verified Working Flow
1. Discover speakers:
   - `python sonos_spotify_cli.py devices`
2. Run one-time SoCo Spotify auth:
   - `python sonos_spotify_cli.py auth-spotify --speaker "Coffee Room"`
3. Search:
   - `python sonos_spotify_cli.py search "daft punk one more time" --speaker "Coffee Room"`
4. Play:
   - `python sonos_spotify_cli.py play "daft punk one more time" --speaker "Coffee Room" --pick`

## Known Gaps
- Some search results are broad/noisy.
- Artist/album metadata may show as `Unknown` for some items returned by Sonos service.
- Playlist browsing is not yet implemented as a command.

## Next Work Items
1. Add `playlists` command for Spotify playlists.
2. Improve metadata extraction (artist/album fallbacks).
3. Improve play ranking (exact match bias).

## Release Notes (Session)
- Added CLI project scaffolding.
- Added Sonos + Spotify command set.
- Added JSON output and config support.
- Added `auth-spotify` command and compatibility handling for auth return formats.

## 2026-03-04 update
- Added `playlists` command to list Spotify playlists via Sonos.
- Added optional playlist query filter and JSON output.
- Added docs section in README for playlist usage.
- Added `group` and `ungroup` commands for multi-speaker playback.
- Group model: play on coordinator controls all grouped speakers.
