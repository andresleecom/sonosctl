# sonosctl

A Python CLI for controlling Sonos speakers and Spotify playback on a local network.

Related documentation:
- Technical context and change log: `docs/SONOS_CLI_CONTEXT.md`
- Deployment and operations runbook: `docs/DEPLOYMENT_RUNBOOK.md`
- Daily operator quick guide: `docs/OPERATOR_GUIDE.md`

## Features

- Discover Sonos speakers on LAN
- Search Spotify tracks through Sonos
- Play tracks with optional interactive selection (`--pick`)
- List Spotify playlists
- Show live playback status (`status`)
- View and manage playback queue (`queue`, `queue add`, `queue clear`)
- Play full Spotify playlists by name or ID (`play-playlist`)
- Playback controls (`pause`, `resume`, `next`, `prev`)
- Crossfade mode control (`crossfade`)
- Volume control
- Multi-room grouping (`group`, `ungroup`)
- JSON output for scripting (`devices`, `search`, `playlists`)
- Default config via `~/.sonosctl/config.toml`
- One-time CLI Spotify auth helper (`auth-spotify`)

## Requirements

- Python `3.10+`
- Sonos speakers and control machine on the same LAN/VLAN
- Spotify added in Sonos app
- Local network access to Sonos devices

## Installation

### Option A: Local development install

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

### Option B: End-user install (recommended)

```bash
pipx install .
```

If published to PyPI:

```bash
pipx install sonos-spotify-cli
```

## First-time setup

1. Discover speakers:

```bash
sonosctl devices
```

2. Run one-time Spotify auth for this environment:

```bash
sonosctl auth-spotify --speaker "Living Room"
```

3. Validate with search:

```bash
sonosctl search "daft punk one more time" --speaker "Living Room"
```

## Common commands

### Discovery

```bash
sonosctl devices
sonosctl devices --json
```

### Search and play

```bash
sonosctl search "nujabes feather" --speaker "Living Room"
sonosctl search "nujabes feather" --json --speaker "Living Room"
sonosctl play "nujabes feather" --speaker "Living Room"
sonosctl play "nujabes feather" --speaker "Living Room" --pick --limit 10
```

### Playlists

```bash
sonosctl playlists --speaker "Living Room"
sonosctl playlists chill --speaker "Living Room"
sonosctl playlists --speaker "Living Room" --json
```

### Playlist playback

```bash
sonosctl play-playlist "Chill Vibes" --speaker "Living Room"
sonosctl play-playlist "Chill Vibes" --speaker "Living Room" --shuffle
sonosctl play-playlist "spotify:user:spotify:playlist:0FQk6BADgIIYd3yTLCThjg" --speaker "Living Room"
sonosctl play-playlist "Chill Vibes" --speaker "Living Room" --keep-queue
```

### Playback controls

```bash
sonosctl status --speaker "Living Room"
sonosctl status --speaker "Living Room" --json
sonosctl pause --speaker "Living Room"
sonosctl resume --speaker "Living Room"
sonosctl next --speaker "Living Room"
sonosctl prev --speaker "Living Room"
sonosctl volume --speaker "Living Room"
sonosctl volume 35 --speaker "Living Room"
```

### Multi-room grouping

```bash
sonosctl group --coordinator "Living Room" --members "Office"
sonosctl play "daft punk one more time" --speaker "Living Room" --pick
sonosctl ungroup --speaker "Office"
```

### Queue management

```bash
sonosctl queue --speaker "Living Room"
sonosctl queue --speaker "Living Room" --json
sonosctl queue add "nujabes feather" --speaker "Living Room"
sonosctl queue add "nujabes feather" --speaker "Living Room" --pick --limit 10
sonosctl queue clear --speaker "Living Room"
```

### Playback modes

```bash
sonosctl shuffle --speaker "Living Room"
sonosctl shuffle on --speaker "Living Room"
sonosctl shuffle off --speaker "Living Room"

sonosctl repeat --speaker "Living Room"
sonosctl repeat all --speaker "Living Room"
sonosctl repeat one --speaker "Living Room"
sonosctl repeat off --speaker "Living Room"

sonosctl crossfade --speaker "Living Room"
sonosctl crossfade on --speaker "Living Room"
sonosctl crossfade off --speaker "Living Room"
```

## Configuration

Default config path: `~/.sonosctl/config.toml`

Example:

```toml
[defaults]
speaker = "Living Room"
timeout = 5
search_limit = 8
replace_queue = false
json = false
```

Override config file path:

```bash
sonosctl --config C:\path\to\config.toml devices
```

## Troubleshooting

### `AuthTokenExpired`

```bash
sonosctl auth-spotify --speaker "Living Room"
```

Then retry with explicit speaker:

```bash
sonosctl search "test" --speaker "Living Room"
```

### `No Sonos speakers found on your network`

- Confirm same LAN/VLAN
- Disable local VPN
- Check AP/router client isolation settings
- Increase timeout:

```bash
sonosctl devices --timeout 15
```

### Invalid auth link code

- Run `auth-spotify` again
- Use the new code immediately
- Avoid browser contexts that block login/session handoff

## Release and distribution

Build and publish:

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine upload dist/*
```

Install from PyPI:

```bash
pipx install sonos-spotify-cli
```

## Help

```bash
sonosctl --help
sonosctl play --help
sonosctl playlists --help
```

## Security and Licensing

- License: `MIT` (see `LICENSE`)
- Vulnerability reporting: `SECURITY.md`
- Pre-release hardening: `docs/HARDENING_CHECKLIST.md`

