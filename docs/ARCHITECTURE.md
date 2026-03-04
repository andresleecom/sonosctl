# Architecture

## Overview

sonosctl is a single-file Python CLI that controls Sonos speakers and Spotify playback over a local network.

## Stack

- **Language**: Python 3.10+
- **Core library**: [SoCo](https://github.com/SoCo/SoCo) — Sonos control
- **Config**: TOML (`~/.sonosctl/config.toml`)
- **Packaging**: pyproject.toml, entry point `sonosctl`

## File structure

```
sonos_spotify_cli.py   # All CLI logic (single module)
pyproject.toml         # Package config and dependencies
docs/                  # Architecture and hardening docs
```

## Design

### Single module

All logic lives in `sonos_spotify_cli.py`. This is intentional — the tool is small enough that splitting into packages adds complexity without value.

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
