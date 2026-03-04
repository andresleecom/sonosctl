# Sonos CLI Context Log

Last updated: 2026-03-04

## Goal
Build and validate a local CLI tool to control Sonos speakers and Spotify playback on the same LAN.

## Current Status
- Sonos discovery works.
- Spotify search and playback work after SoCo authorization.
- Multi-speaker discovery confirmed:
  - `Living Room` (`192.168.68.110`)
  - `Office` (`192.168.68.106`)

## Architecture
- Language: Python
- Core library: `soco`
- Entry point: `sonos_spotify_cli.py`
- Package config: `pyproject.toml`
- Main docs: `README.md`

## Implemented Commands
- `devices`
- `search`
- `playlists`
- `play`
- `play-playlist`
- `shuffle`
- `repeat`
- `crossfade`
- `status`
- `queue`
- `group`
- `ungroup`
- `auth-spotify`
- `pause`
- `resume`
- `next`
- `prev`
- `volume`

## Implemented Features
- JSON output:
  - `devices --json`
  - `search --json`
  - `playlists --json`
- Interactive selection:
  - `play --pick`
- Config defaults in `~/.sonosctl/config.toml`
- Speaker-scoped Spotify service usage for `search` and `play`
- Multi-room grouping and ungrouping
- Live playback status command (`status`) with JSON output
- Queue management commands (`queue`, `queue add`, `queue clear`)
- Crossfade mode control (`crossfade`)

## Auth and Token Notes
Observed error during development:
- `Authorization for Spotify expired, is invalid or has not yet been completed: [ns0:Client.AuthTokenExpired / authTokenExpired / None]`

Resolution:
- Added `auth-spotify` command to run SoCo device-link flow.

Important behavior:
- `begin_authentication()` returned different response shapes depending on runtime:
  - tuple/list
  - dict
  - URL string only

CLI now supports all formats and extracts `linkCode` from URL query when required.

## Verified Working Flow
1. Discover speakers:
   - `python sonos_spotify_cli.py devices`
2. Authorize Spotify once:
   - `python sonos_spotify_cli.py auth-spotify --speaker "Living Room"`
3. Search:
   - `python sonos_spotify_cli.py search "daft punk one more time" --speaker "Living Room"`
4. Play:
   - `python sonos_spotify_cli.py play "daft punk one more time" --speaker "Living Room" --pick`
5. Group rooms and play multi-room:
   - `python sonos_spotify_cli.py group --coordinator "Living Room" --members "Office"`

## Known Gaps
- Search ranking can return broad matches.
- Artist/album metadata may be `Unknown` for some Sonos responses.

## Suggested Next Improvements
1. Add stronger result ranking (exact match bias).
2. Improve metadata parsing fallbacks.
3. Add advanced queue operations (remove/reorder specific items).

## Session Summary
- Scaffolded Python CLI project.
- Implemented Sonos + Spotify control commands.
- Added JSON output and config support.
- Added robust `auth-spotify` flow compatibility.
- Added playlists and multi-room group operations.
- Added deployment and operator documentation.
- Added `status` command and fixed duplicate track-search call in `play`.
- Added `queue` commands (list/add/clear) for non-interruptive queue management.
- Added `play-playlist` command to start full Spotify playlists by name or ID.
- Added `shuffle` and `repeat` commands with state-query and set-mode support.
- Added `crossfade` command with state-query and on/off control.

