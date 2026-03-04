# Sonos CLI Deployment Runbook

Last updated: 2026-03-04

## Objective
Desplegar y operar el CLI en otro entorno para que varios usuarios controlen música en bocinas Sonos.

## Scope
- Instalación
- Onboarding de usuarios
- Operación diaria
- Incidentes comunes

## 1. Pre-deployment Checklist

- [ ] Sonos visible y funcional en Sonos app
- [ ] Spotify agregado en Sonos app
- [ ] Host de control en la misma LAN/VLAN que Sonos
- [ ] Firewall local permite tráfico saliente a LAN
- [ ] Python 3.10+ instalado
- [ ] `pipx` instalado para usuarios finales

## 2. Install on Control Host

```bash
pipx install sonos-spotify-cli
```

Si se instala desde repo local:

```bash
pipx install .
```

Verify:

```bash
sonosctl --help
sonosctl devices
```

## 3. First-time Authorization (per environment)

Run once:

```bash
sonosctl auth-spotify --speaker "Coffee Room"
```

Process:
1. Open URL shown in terminal
2. Enter code shown
3. Login in Spotify and approve
4. Return terminal and confirm

Validation:

```bash
sonosctl search "daft punk one more time" --speaker "Coffee Room"
```

## 4. Team User Onboarding

Per user config at `~/.sonosctl/config.toml`:

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

## 5. Daily Operations

Single speaker playback:

```bash
sonosctl play "track name" --speaker "Coffee Room" --pick
```

Group playback:

```bash
sonosctl group --coordinator "Coffee Room" --members "Dining Room"
sonosctl play "track name" --speaker "Coffee Room" --pick
```

Ungroup:

```bash
sonosctl ungroup --speaker "Dining Room"
```

## 6. Operational Safety Rules

- Always set `--speaker` (or config default) in shared environments
- Avoid running control commands from multiple terminals at once
- Use one coordinator room for grouped playback
- Keep auth/session tasks to designated operator/admin

## 7. Incident Response

### A) `AuthTokenExpired`

1. Re-run auth:

```bash
sonosctl auth-spotify --speaker "Coffee Room"
```

2. Retest with explicit speaker:

```bash
sonosctl search "test" --speaker "Coffee Room"
```

### B) Speakers not discovered

```bash
sonosctl devices --timeout 15
```

If still empty:
- Check VLAN/AP isolation
- Disable local VPN
- Confirm Sonos app can play from same network

### C) Group commands fail

- Verify exact speaker names from `sonosctl devices`
- Recreate group explicitly

```bash
sonosctl group --coordinator "Coffee Room" --members "Dining Room"
```

## 8. Upgrade Procedure

If installed with pipx from PyPI:

```bash
pipx upgrade sonos-spotify-cli
```

If installed from local path/repo:

```bash
pipx reinstall sonos-spotify-cli
```

Run post-upgrade checks:

```bash
sonosctl --help
sonosctl devices
sonosctl search "test" --speaker "Coffee Room"
```

## 9. Rollback Strategy

- Keep previous release tag/wheel in internal artifact store.
- Reinstall previous known-good version with pipx.
- Re-run smoke tests from section 8.

## 10. Support Data to Capture

When reporting issues include:
- Command run
- Full CLI error output
- `sonosctl devices` output
- Speaker targeted
- Whether Sonos app can play Spotify at same moment
