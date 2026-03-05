# sonosctl

Control your Sonos speakers and Spotify from the terminal.

> sonosctl is an independent tool created by Andres Lee for personal automation workflows. It is not made by, affiliated with, endorsed by, or sponsored by Sonos or Spotify.


[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CI](https://github.com/andresleecom/sonosctl/actions/workflows/ci.yml/badge.svg)](https://github.com/andresleecom/sonosctl/actions/workflows/ci.yml)

<p align="center">
  <img src="docs/assets/sonosctl.png" alt="Clawde the DJ Lobster" width="180" />
</p>

<p align="center"><em>Command the vibe.</em></p>

```
$ sonosctl devices
Living Room | 192.168.68.110 | Sonos One
Office      | 192.168.68.106 | Sonos One

$ sonosctl play "nujabes feather" --speaker "Living Room"
Now playing on Living Room: Feather - Nujabes (Modal Soul)

$ sonosctl status
Speaker: Living Room
State: PLAYING
Track: Feather
Artist: Nujabes
Album: Modal Soul
Position: 0:01:23 / 0:04:47
Volume: 25

$ sonosctl queue add "khruangbin evan finds the third room"
Added to queue: Evan Finds the Third Room - Khruangbin

$ sonosctl group --coordinator "Living Room" --members "Office"
Grouped: Office -> Living Room
```

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
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

## Quick start

**1. Discover speakers**

```bash
sonosctl devices
```

**2. Authenticate Spotify** (one-time per speaker)

```bash
sonosctl auth-spotify --speaker "Living Room"
```

Open the link, authorize, then press Enter.

**3. Play something**

```bash
sonosctl play "bohemian rhapsody"
```

## Commands

### Playback

| Command | Description |
|---------|-------------|
| `play <query>` | Search and play a track |
| `play-playlist <name>` | Play a Spotify playlist by name |
| `pause` | Pause playback |
| `resume` | Resume playback |
| `next` | Skip to next track |
| `prev` | Previous track |
| `volume [level]` | Get or set volume (0-100) |
| `status` | Show current track, position, volume |

### Queue

| Command | Description |
|---------|-------------|
| `queue` | Show playback queue |
| `queue add <query>` | Add a track without interrupting |
| `queue clear` | Clear the queue |

### Search & Browse

| Command | Description |
|---------|-------------|
| `search <query>` | Search Spotify tracks |
| `playlists [query]` | List or search playlists |
| `favorites [all\|playlists\|tracks] [query]` | List Sonos favorites, including favorite playlists and songs |

### Playback modes

| Command | Description |
|---------|-------------|
| `shuffle [on\|off]` | Toggle shuffle mode |
| `repeat [off\|one\|all]` | Set repeat mode |
| `crossfade [on\|off]` | Toggle crossfade between tracks |

### Multi-room & Setup

| Command | Description |
|---------|-------------|
| `devices` | Discover speakers on your network |
| `group` | Group speakers for synchronized playback |
| `ungroup` | Remove a speaker from its group |
| `groups` | Show current Sonos group topology |
| `doctor status` | Analyze captured `status --json --raw` diagnostics |
| `auth-spotify` | One-time Spotify authorization |

Most commands accept `--speaker`, `--json`, and `--timeout`. Run `sonosctl <command> --help` for details.

## Configuration

Create `~/.sonosctl/config.toml` to set defaults:

```toml
[defaults]
speaker = "Living Room"
timeout = 5
search_limit = 8
```

With a default speaker configured, you can omit `--speaker` from all commands.

## Automation

sonosctl is designed for scripting and automation. JSON output on every major command:

```bash
sonosctl status --json | jq '.track'
sonosctl queue --json | jq '.items[].title'
```

Pair it with cron for scheduled playback:

```bash
# Morning playlist at 8 AM
0 8 * * * sonosctl play-playlist "Morning Chill" --shuffle

# Lower volume at 10 PM
0 22 * * * sonosctl volume 10
```

## Troubleshooting

**`AuthTokenExpired`** - Re-run `sonosctl auth-spotify --speaker "Living Room"`.

**No speakers found** - Verify same LAN/VLAN, disable VPN, try `sonosctl devices --timeout 15`.

**Auth link not working** - Run `auth-spotify` again and use the new code immediately.

**Group/ungroup looks stuck** - verify actual topology and use wait-confirmation:

```bash
sonosctl group --coordinator "Living Room" --members "Office" --wait 3
sonosctl ungroup --speaker "Office" --wait 3
sonosctl groups
```

**`status` returns `Unknown` intermittently** - capture raw payloads and run diagnostics:

```bash
# collect
1..60 | % { python -m sonosctl status --speaker "Living Room" --json --raw; Start-Sleep 2 } | Set-Content status-debug.jsonl

# analyze
python -m sonosctl doctor status --input status-debug.jsonl --samples 10
```

## Requirements

- Python 3.10+
- Sonos speakers on the same local network
- Spotify linked in the Sonos app

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Open Source Project Files

- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [SECURITY.md](SECURITY.md)
- [CHANGELOG.md](CHANGELOG.md)
- [docs/AI_AGENT_INTEGRATION.md](docs/AI_AGENT_INTEGRATION.md)

## Independence Notice

sonosctl is completely independent from Sonos and Spotify.
It was built by Andres Lee to solve real-world personal automation problems.

All product and company names, including Sonos and Spotify, are trademarks of their respective owners.

## License

MIT - see [LICENSE](LICENSE).

---

Made with love from Cancun.



