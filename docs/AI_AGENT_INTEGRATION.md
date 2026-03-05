# AI Agent Integration

`sonosctl` is designed to be agent-friendly. AI agents (including OpenClaw-style automations)
can call commands in non-interactive mode and parse JSON responses.

## Recommended command patterns

- Device discovery:
  - `sonosctl devices --json`
- Playback status:
  - `sonosctl status --json --speaker "Living Room"`
- Queue state:
  - `sonosctl queue --json --speaker "Living Room"`
- Search candidates:
  - `sonosctl search "query" --json --speaker "Living Room"`
- Playlist catalog:
  - `sonosctl playlists --json --speaker "Living Room"`
- Favorites catalog:
  - `sonosctl favorites playlists --json --speaker "Living Room"`
  - `sonosctl favorites tracks --json --speaker "Living Room"`

## Non-interactive best practices

- Prefer explicit speaker targeting with `--speaker`.
- Avoid `--pick` in automation workflows.
- Use idempotent reads before writes:
  1. `status --json`
  2. `queue --json`
  3. decide action
- Treat non-zero exit codes as command failure.

## Safe operation guidelines

- Restrict agent execution to a trusted host on same LAN as Sonos.
- Keep one active controller per room/group to reduce race conditions.
- Re-auth via `auth-spotify` if `AuthTokenExpired` occurs.

## Example flow

```bash
sonosctl devices --json
sonosctl status --json --speaker "Living Room"
sonosctl play-playlist "Morning Chill" --speaker "Living Room" --shuffle
sonosctl queue --json --speaker "Living Room"
```
