# Sonos CLI Deployment Runbook

Last updated: 2026-03-04

## Objective
Deploy and operate `sonosctl` in a shared environment where multiple users manage Sonos speaker playback.

## Scope
- Installation
- User onboarding
- Daily operations
- Incident response
- Upgrade and rollback

## 1. Pre-deployment checklist

- [ ] Sonos system is visible and functional in Sonos app
- [ ] Spotify is added in Sonos app
- [ ] Control host is on same LAN/VLAN as Sonos
- [ ] Local firewall allows outbound LAN traffic
- [ ] Python 3.10+ installed
- [ ] `pipx` installed for end users

## 2. Install on control host

From PyPI:

```bash
pipx install sonos-spotify-cli
```

From local repository:

```bash
pipx install .
```

Validation:

```bash
sonosctl --help
sonosctl devices
```

## 3. First-time authorization (per environment)

Run once:

```bash
sonosctl auth-spotify --speaker "Coffee Room"
```

Process:
1. Open URL shown in terminal
2. Enter code shown
3. Sign in to Spotify and approve
4. Return to terminal and confirm

Validation:

```bash
sonosctl search "daft punk one more time" --speaker "Coffee Room"
```

## 4. Team user onboarding

Per-user config at `~/.sonosctl/config.toml`:

```toml
[defaults]
speaker = "Coffee Room"
timeout = 5
search_limit = 8
replace_queue = false
json = false
```

Quick validation per user:

```bash
sonosctl devices
sonosctl search "test" --speaker "Coffee Room"
```

## 5. Daily operations

Single-room playback:

```bash
sonosctl play "track name" --speaker "Coffee Room" --pick
```

Multi-room playback:

```bash
sonosctl group --coordinator "Coffee Room" --members "Dining Room"
sonosctl play "track name" --speaker "Coffee Room" --pick
```

Ungroup:

```bash
sonosctl ungroup --speaker "Dining Room"
```

## 6. Operational safety rules

- Always set `--speaker` (or define config default) in shared usage
- Avoid issuing control commands from multiple terminals simultaneously
- Use one standard coordinator speaker for grouped playback
- Keep auth/session actions restricted to designated operators

## 7. Incident response

### A) `AuthTokenExpired`

```bash
sonosctl auth-spotify --speaker "Coffee Room"
sonosctl search "test" --speaker "Coffee Room"
```

### B) Speakers not discovered

```bash
sonosctl devices --timeout 15
```

If still empty:
- Check VLAN/AP isolation
- Disable local VPN
- Confirm Sonos app playback on same network

### C) Group commands fail

- Verify exact speaker names from `sonosctl devices`
- Recreate group explicitly:

```bash
sonosctl group --coordinator "Coffee Room" --members "Dining Room"
```

## 8. Upgrade procedure

If installed from PyPI:

```bash
pipx upgrade sonos-spotify-cli
```

If installed from local repo:

```bash
pipx reinstall sonos-spotify-cli
```

Post-upgrade checks:

```bash
sonosctl --help
sonosctl devices
sonosctl search "test" --speaker "Coffee Room"
```

## 9. Rollback strategy

- Keep previous release tags/wheels in artifact storage
- Reinstall previous known-good version with `pipx`
- Re-run smoke checks from section 8

## 10. Support data to capture

When escalating issues, include:
- Command executed
- Full CLI error output
- `sonosctl devices` output
- Target speaker
- Whether Spotify playback works in Sonos app at the same time
