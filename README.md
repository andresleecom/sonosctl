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
- Playback controls (`pause`, `resume`, `next`, `prev`)
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
sonosctl auth-spotify --speaker "Coffee Room"
```

3. Validate with search:

```bash
sonosctl search "daft punk one more time" --speaker "Coffee Room"
```

## Common commands

### Discovery

```bash
sonosctl devices
sonosctl devices --json
```

### Search and play

```bash
sonosctl search "nujabes feather" --speaker "Coffee Room"
sonosctl search "nujabes feather" --json --speaker "Coffee Room"
sonosctl play "nujabes feather" --speaker "Coffee Room"
sonosctl play "nujabes feather" --speaker "Coffee Room" --pick --limit 10
```

### Playlists

```bash
sonosctl playlists --speaker "Coffee Room"
sonosctl playlists chill --speaker "Coffee Room"
sonosctl playlists --speaker "Coffee Room" --json
```

### Playback controls

```bash
sonosctl pause --speaker "Coffee Room"
sonosctl resume --speaker "Coffee Room"
sonosctl next --speaker "Coffee Room"
sonosctl prev --speaker "Coffee Room"
sonosctl volume --speaker "Coffee Room"
sonosctl volume 35 --speaker "Coffee Room"
```

### Multi-room grouping

```bash
sonosctl group --coordinator "Coffee Room" --members "Dining Room"
sonosctl play "daft punk one more time" --speaker "Coffee Room" --pick
sonosctl ungroup --speaker "Dining Room"
```

## Configuration

Default config path: `~/.sonosctl/config.toml`

Example:

```toml
[defaults]
speaker = "Coffee Room"
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
sonosctl auth-spotify --speaker "Coffee Room"
```

Then retry with explicit speaker:

```bash
sonosctl search "test" --speaker "Coffee Room"
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
