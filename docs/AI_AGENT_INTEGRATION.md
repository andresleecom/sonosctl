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
- Playback history:
  - `sonosctl history --json --speaker "Living Room"`
- Continuous monitor:
  - `sonosctl monitor --speaker "Living Room" --interval 15`
- Group topology:
  - `sonosctl groups --json`
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
  3. `history --json`
  4. decide action
- Treat non-zero exit codes as command failure.
- For flaky metadata, capture raw payloads with `status --json --raw` and analyze with `doctor status`.

## Anti-repetition policy

For music-selection agents, the minimum useful loop is:

1. `sonosctl status --json --speaker "Living Room"`
2. `sonosctl queue --json --speaker "Living Room"`
3. `sonosctl history --json --speaker "Living Room"`
4. Avoid:
   - tracks seen in the last 20 entries
   - artists seen in the last 10 entries
5. Only then select or queue new music

If you want history to stay fresh even when no one manually calls `status`, keep `monitor` running in the background.

## Safe operation guidelines

- Restrict agent execution to a trusted host on same LAN as Sonos.
- Keep one active controller per room/group to reduce race conditions.
- Re-auth via `auth-spotify` if `AuthTokenExpired` occurs.

## Example flow

```bash
sonosctl devices --json
sonosctl groups --json
sonosctl status --json --speaker "Living Room"
sonosctl history --json --speaker "Living Room"
sonosctl play-playlist "Morning Chill" --speaker "Living Room" --shuffle
sonosctl queue --json --speaker "Living Room"
```
