# Sonos CLI - Operator Guide (Daily Shift)

Last updated: 2026-03-04

## Objective
Run Sonos music operations during the day with a simple, repeatable process.

## 1) Shift start checklist (2-3 minutes)

1. Confirm the control laptop/PC is on the same local network as Sonos.
2. Confirm local VPN is OFF.
3. Open terminal.
4. Verify speakers:

```bash
sonosctl devices
```

5. Quick search test:

```bash
sonosctl search "test" --speaker "Coffee Room"
```

If both commands succeed, operations are ready.

## 2) Core commands during shift

Play a track (with interactive selection):

```bash
sonosctl play "track name" --speaker "Coffee Room" --pick
```

Search without playing:

```bash
sonosctl search "track name" --speaker "Coffee Room"
```

Check current playback before transitions:

```bash
sonosctl status --speaker "Coffee Room"
```

Transport and volume:

```bash
sonosctl pause --speaker "Coffee Room"
sonosctl resume --speaker "Coffee Room"
sonosctl next --speaker "Coffee Room"
sonosctl prev --speaker "Coffee Room"
sonosctl volume 35 --speaker "Coffee Room"
```

View playlists:

```bash
sonosctl playlists --speaker "Coffee Room"
sonosctl playlists chill --speaker "Coffee Room"
```

## 3) Multi-speaker operation

Group `Dining Room` into `Coffee Room`:

```bash
sonosctl group --coordinator "Coffee Room" --members "Dining Room"
```

Play on coordinator (audio in both rooms):

```bash
sonosctl play "track name" --speaker "Coffee Room" --pick
```

Ungroup:

```bash
sonosctl ungroup --speaker "Dining Room"
```

## 4) Shift end checklist

1. Set agreed volume level (example 25-35):

```bash
sonosctl volume 30 --speaker "Coffee Room"
```

2. Pause playback or set closing playlist per policy:

```bash
sonosctl pause --speaker "Coffee Room"
```

3. If temporary grouping was used, ungroup speakers:

```bash
sonosctl ungroup --speaker "Dining Room"
```

## 5) Common incidents and quick fixes

### A) `AuthTokenExpired`

Re-authorize:

```bash
sonosctl auth-spotify --speaker "Coffee Room"
sonosctl search "test" --speaker "Coffee Room"
```

### B) No speakers found

1. Confirm same LAN.
2. Confirm VPN is off.
3. Retry with larger timeout:

```bash
sonosctl devices --timeout 15
```

### C) Audio not playing in both rooms

Recreate group:

```bash
sonosctl group --coordinator "Coffee Room" --members "Dining Room"
```

## 6) Operational rules

1. One active operator per shift.
2. Always use exact speaker names from `sonosctl devices`.
3. Use `Coffee Room` as standard multi-room coordinator.
4. If an issue persists, capture command + full error and escalate.

## 7) Quick reference

```bash
sonosctl devices
sonosctl play "daft punk one more time" --speaker "Coffee Room" --pick
sonosctl group --coordinator "Coffee Room" --members "Dining Room"
sonosctl ungroup --speaker "Dining Room"
sonosctl auth-spotify --speaker "Coffee Room"
```

Queue management during shifts:

```bash
sonosctl queue --speaker "Coffee Room"
sonosctl queue add "track name" --speaker "Coffee Room"
```

Playlist mode during shifts:

```bash
sonosctl play-playlist "Chill Vibes" --speaker "Coffee Room" --shuffle
```

Playback mode controls during shifts:

```bash
sonosctl shuffle on --speaker "Coffee Room"
sonosctl repeat all --speaker "Coffee Room"
sonosctl crossfade on --speaker "Coffee Room"
```
