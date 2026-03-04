# Architecture

## Overview

sonosctl is a Python CLI that controls Sonos speakers and Spotify playback over a local network.

## Stack

- **Language**: Python 3.10+
- **Core library**: [SoCo](https://github.com/SoCo/SoCo) — Sonos control
- **Config**: TOML (`~/.sonosctl/config.toml`)
- **Packaging**: pyproject.toml, entry point `sonosctl`

## Package structure

```
sonosctl/
├── __init__.py          # Package version
├── __main__.py          # python -m sonosctl support
├── cli.py               # Argparse tree + main() entry point
├── config.py            # TOML config loading, defaults, effective_*() helpers
├── speaker.py           # Speaker discovery, resolution, with_speaker helper
├── spotify.py           # Spotify service, search, playlist lookup, metadata helpers
├── types.py             # Shared dataclasses (TrackResult, PlaylistResult, etc.)
└── commands/
    ├── __init__.py      # Re-exports all cmd_* functions
    ├── auth.py          # cmd_auth_spotify
    ├── devices.py       # cmd_devices
    ├── group.py         # cmd_group, cmd_ungroup
    ├── modes.py         # cmd_shuffle, cmd_repeat, cmd_crossfade
    ├── playback.py      # cmd_play, cmd_pause, cmd_resume, cmd_next, cmd_prev, cmd_volume, cmd_status
    ├── playlist.py      # cmd_play_playlist
    ├── queue.py         # cmd_queue_list, cmd_queue_add, cmd_queue_clear
    └── search.py        # cmd_search, cmd_playlists
```

## Module responsibilities

- **types.py** — Dataclasses shared across modules. No circular imports.
- **config.py** — TOML config loading + `effective_*()` resolution helpers.
- **speaker.py** — Speaker discovery/resolution. Core infra used by all commands.
- **spotify.py** — Spotify service + search + playlist lookup.
- **commands/** — Each file has 1-3 related command handlers.
- **cli.py** — Argparse tree + `main()`. The wiring layer.

## Dependency flow

```
types.py          (no deps)
config.py         <- types
speaker.py        <- config
spotify.py        <- config, types
commands/*        <- config, speaker, spotify, types
cli.py            <- commands, config
```

Commands import from core modules (`config`, `speaker`, `spotify`), never from each other
(except `queue.py` imports `prompt_track_selection` from `playback.py`).

## Design

### Command pattern

Each command is a `cmd_<name>(args)` function wired via argparse subparsers. The entry point is `main(argv)` which builds the parser and dispatches.

### Config cascading

CLI args > config file > hardcoded defaults. The `effective_*()` helpers merge these layers.

### Speaker resolution

`resolve_speaker()` finds a speaker by name (exact or partial match), IP, or auto-selects if only one device exists on the network.

### Spotify integration

SoCo's `MusicService` handles Spotify search and playback through the Sonos device's own Spotify account. This means:

- No Spotify API keys needed
- Auth is per-speaker, stored by SoCo
- Search results come from Sonos's Spotify service, not the Spotify API directly

### Auth flow

`auth-spotify` runs a device-link flow where the user opens a URL, authorizes in browser, and the CLI confirms. The `begin_authentication()` response varies by runtime (tuple, dict, or URL string) — the CLI handles all formats.

## Commands (17)

`devices`, `search`, `playlists`, `play`, `play-playlist`, `shuffle`, `repeat`, `crossfade`, `status`, `queue` (list/add/clear), `group`, `ungroup`, `auth-spotify`, `pause`, `resume`, `next`, `prev`, `volume`

## Known limitations

- Search ranking can return broad matches for short queries
- Artist/album metadata may be `Unknown` for some Sonos responses
- Queue operations are append-only (no reorder/remove individual items)
