# sonosctl

Programmable home audio.

`sonosctl` is a terminal-first, local-first CLI for controlling Sonos speakers and Spotify from scripts, cron jobs, shortcuts, and AI agents.

It is built for people who want home audio to be automatable, composable, and easy to integrate into local workflows.

> `sonosctl` is an independent open source project by Andres Lee. It is not affiliated with, endorsed by, or sponsored by Sonos or Spotify.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CI](https://github.com/andresleecom/sonosctl/actions/workflows/ci.yml/badge.svg)](https://github.com/andresleecom/sonosctl/actions/workflows/ci.yml)

<p align="center">
  <img src="docs/assets/sonosctl.png" alt="Clawde the DJ Lobster" width="180" />
</p>

<p align="center"><em>Command the vibe.</em></p>

```bash
$ sonosctl devices
Living Room | 192.168.68.110 | Sonos One
Office      | 192.168.68.106 | Sonos One

$ sonosctl play "nujabes feather" --speaker "Living Room"
Now playing on Living Room: Feather - Nujabes

$ sonosctl status --speaker "Living Room"
Speaker: Living Room
State: PLAYING
Track: Feather
Artist: Nujabes
Album: Modal Soul
Position: 0:01:23 / 0:04:47
Volume: 25
Source: x-sonos-spotify:spotify%3atrack%3a...

$ sonosctl queue add "khruangbin evan finds the third room" --speaker "Living Room"
Added to queue on Living Room: Evan Finds the Third Room - Khruangbin (position 12)

$ sonosctl group --coordinator "Living Room" --members "Office"
Grouped with coordinator Living Room: Office
```

## Why sonosctl?

Most Sonos control flows are built for apps and taps.

`sonosctl` is built for automation.

Use it when you want to:

- start music from a shell script
- trigger playback from cron
- wire Sonos into Raycast, Shortcuts, Stream Deck, or Alfred
- expose local speaker control to AI agents
- inspect playback state as JSON
- manage speakers from a terminal without opening the Sonos app

## Features

- Discover Sonos speakers on your LAN
- Play tracks and playlists from Spotify through Sonos
- Read playback state, queue contents, and group topology
- Group and ungroup rooms
- Toggle shuffle, repeat, and crossfade
- Output JSON on automation-oriented commands
- Run locally with no Spotify developer API keys

## Install

```bash
pipx install sonosctl
```

Or with pip:

```bash
pip install sonosctl
```

From source:

```bash
git clone https://github.com/andresleecom/sonosctl.git
cd sonosctl
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Quick Start

### 1. Discover speakers

```bash
sonosctl devices
```

### 2. Authenticate Spotify

Spotify auth is usually a one-time setup per Sonos household.

```bash
sonosctl auth-spotify --speaker "Living Room"
```

Open the link, approve access, then press Enter to complete linking.

### 3. Play something

```bash
sonosctl play "bohemian rhapsody" --speaker "Living Room"
```

### 4. Use JSON in scripts

```bash
sonosctl status --speaker "Living Room" --json | jq '.track'
sonosctl queue --speaker "Living Room" --json | jq '.items[].title'
```

## Automation Use Cases

### Cron

```bash
# Morning playlist at 8 AM
0 8 * * * sonosctl play-playlist "Morning Chill" --speaker "Living Room" --shuffle

# Lower volume at 10 PM
0 22 * * * sonosctl volume 10 --speaker "Living Room"
```

### Shell scripts

```bash
#!/usr/bin/env bash
set -euo pipefail

current_track="$(sonosctl status --speaker "Living Room" --json | jq -r '.track')"
echo "Now playing: $current_track"
```

### AI agents and local tools

`sonosctl` works well as a thin control layer for:

- local AI agents
- Raycast scripts
- Stream Deck actions
- Apple Shortcuts
- shell aliases and desktop automations

See [docs/AI_AGENT_INTEGRATION.md](docs/AI_AGENT_INTEGRATION.md).

## Commands

### Playback

| Command | Description |
|---------|-------------|
| `play <query>` | Search and play the first Spotify track match |
| `play-playlist <name-or-id>` | Play a Spotify playlist by name or item ID |
| `pause` | Pause playback |
| `resume` | Resume playback |
| `next` | Skip to next track |
| `prev` | Go to previous track |
| `volume [level]` | Get or set volume (0-100) |
| `status` | Show current playback state and metadata |

### Queue

| Command | Description |
|---------|-------------|
| `queue` | Show playback queue |
| `queue add <query>` | Add a Spotify track to the queue |
| `queue clear` | Clear the queue |

### Search and Browse

| Command | Description |
|---------|-------------|
| `search <query>` | Search Spotify tracks |
| `playlists [query]` | List or filter playlists |
| `playlist-info <name-or-id>` | Show playlist metadata and tracks |
| `favorites [all\|playlists\|tracks] [query]` | List Sonos favorites |

### Playback Modes

| Command | Description |
|---------|-------------|
| `shuffle [on\|off]` | Show or set shuffle mode |
| `repeat [off\|one\|all]` | Show or set repeat mode |
| `crossfade [on\|off]` | Show or set crossfade mode |

### Multi-room and Diagnostics

| Command | Description |
|---------|-------------|
| `devices` | Discover speakers on your network |
| `group` | Group speakers under a coordinator |
| `ungroup` | Remove a speaker from its group |
| `groups` | Show current Sonos group topology |
| `doctor status` | Analyze captured `status --json --raw` diagnostics |
| `auth-spotify` | Run Spotify linking flow through Sonos |

Run `sonosctl <command> --help` for details.

## Configuration

Create `~/.sonosctl/config.toml` to set defaults:

```toml
[defaults]
speaker = "Living Room"
timeout = 5
search_limit = 8
json = true
```

With a default speaker configured, you can omit `--speaker` from commands that target a specific device.

## JSON Output

These commands support `--json` for automation workflows:

- `devices`
- `search`
- `playlists`
- `favorites`
- `playlist-info`
- `shuffle`
- `repeat`
- `crossfade`
- `queue`
- `status`
- `groups`

Example:

```bash
sonosctl status --speaker "Living Room" --json
sonosctl devices --json
```

## Troubleshooting

**`AuthTokenExpired`**

Re-run:

```bash
sonosctl auth-spotify --speaker "Living Room"
```

**No speakers found**

Verify the speaker is online, on the same LAN/VLAN, and that a VPN is not interfering.

Try:

```bash
sonosctl devices --timeout 15
```

**Auth link not working**

Run `auth-spotify` again and use the new code immediately.

**Group or ungroup looks stuck**

Verify actual topology and use wait confirmation:

```bash
sonosctl group --coordinator "Living Room" --members "Office" --wait 3
sonosctl ungroup --speaker "Office" --wait 3
sonosctl groups
```

**`status` returns `Unknown` intermittently**

Capture raw payloads and run diagnostics:

```bash
for i in $(seq 1 60); do
  python -m sonosctl status --speaker "Living Room" --json --raw
  sleep 2
done > status-debug.jsonl

python -m sonosctl doctor status --input status-debug.jsonl --samples 10
```

## Requirements

- Python 3.10+
- Sonos speakers on the same local network
- Spotify linked in the Sonos app

## Project Docs

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [SECURITY.md](SECURITY.md)
- [CHANGELOG.md](CHANGELOG.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/AI_AGENT_INTEGRATION.md](docs/AI_AGENT_INTEGRATION.md)
- [docs/HARDENING_CHECKLIST.md](docs/HARDENING_CHECKLIST.md)

## Independence Notice

`sonosctl` is completely independent from Sonos and Spotify.

All product and company names, including Sonos and Spotify, are trademarks of their respective owners.

## License

MIT. See [LICENSE](LICENSE).

---

Built by Andres Lee in Cancun.
