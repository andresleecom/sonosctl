# Architecture

## Overview

`sonosctl` is a Python CLI that controls Sonos speakers and Spotify playback over a local network.

## Stack

- Language: Python 3.10+
- Core library: [SoCo](https://github.com/SoCo/SoCo)
- Config: TOML (`~/.sonosctl/config.toml`)
- Packaging: `pyproject.toml`, entry point `sonosctl`

## Package Structure

```text
sonosctl/
|-- __init__.py          # Package version
|-- __main__.py          # python -m sonosctl support
|-- cli.py               # Argparse tree + main() entry point
|-- config.py            # TOML config loading, defaults, effective_* helpers
|-- history.py           # Playback history persistence (JSONL)
|-- speaker.py           # Speaker discovery, resolution, with_speaker helper
|-- spotify.py           # Spotify service, search, playlists, favorites, metadata helpers
|-- types.py             # Shared dataclasses
`-- commands/
    |-- __init__.py      # Re-exports all cmd_* handlers
    |-- auth.py          # cmd_auth_spotify
    |-- devices.py       # cmd_devices
    |-- doctor.py        # cmd_doctor_status
    |-- favorites.py     # cmd_favorites
    |-- group.py         # cmd_group, cmd_ungroup, cmd_groups
    |-- history.py       # cmd_history
    |-- modes.py         # cmd_shuffle, cmd_repeat, cmd_crossfade
    |-- monitor.py       # cmd_monitor
    |-- playback.py      # cmd_play, cmd_pause, cmd_resume, cmd_next, cmd_prev, cmd_volume, cmd_status
    |-- playlist.py      # cmd_play_playlist
    |-- queue.py         # cmd_queue_list, cmd_queue_add, cmd_queue_clear
    `-- search.py        # cmd_search, cmd_playlists
```

## Module Responsibilities

- `types.py`: Dataclasses shared across modules.
- `config.py`: TOML loading + effective value resolution (`effective_*`).
- `history.py`: JSONL persistence for recently observed playback.
- `speaker.py`: Speaker discovery/resolution infrastructure.
- `spotify.py`: Spotify queries + Sonos favorites extraction.
- `commands/*`: Domain command handlers.
- `cli.py`: Parser and command wiring.

## Dependency Flow

```text
types.py          (no deps)
config.py         <- types
history.py        <- config
speaker.py        <- config
spotify.py        <- config, types
commands/*        <- config, history, speaker, spotify, types
cli.py            <- commands, config
```

Commands import from core modules (`config`, `speaker`, `spotify`) and avoid tight coupling.

## Design Notes

### Command Pattern

Each command is a `cmd_<name>(args)` function bound in argparse subparsers.

### Config Cascading

Priority order:

1. CLI args
2. Config file
3. Hardcoded defaults

### Speaker Resolution

`resolve_speaker()` supports exact/partial name match, direct IP, or auto-select when only one speaker is available.

### Spotify Integration

SoCo `MusicService` handles Spotify interactions through Sonos integration:

- No Spotify API keys required in this CLI
- Auth is device/household-scoped via Sonos
- Search results are Sonos/Spotify service responses

### Favorites Integration

`favorites` is sourced from Sonos Favorites (`speaker.music_library.get_sonos_favorites`) and supports filtering for favorite playlists and favorite tracks.

### Playback History

Playback history is stored in `~/.sonosctl/history.jsonl`.

- `status` records newly observed `PLAYING` tracks
- `monitor` keeps history alive in the background by polling a target speaker
- `history` exposes recent entries for agents and automation workflows

This is intended as a lightweight memory layer for anti-repetition logic and automation state.

## Commands (23)

`devices`, `search`, `playlists`, `favorites`, `history`, `monitor`, `play`, `play-playlist`, `shuffle`, `repeat`, `crossfade`, `status`, `queue` (list/add/clear), `group`, `ungroup`, `groups`, `doctor status`, `auth-spotify`, `pause`, `resume`, `next`, `prev`, `volume`

## Known Limitations

- Search ranking can still return broad matches for short queries.
- Artist/album metadata may be `Unknown` for some Sonos responses.
- Queue operations are append/clear (no native reorder/remove by index yet).
- Playback history is observation-based; without `status` calls or `monitor`, no new entries are recorded.
