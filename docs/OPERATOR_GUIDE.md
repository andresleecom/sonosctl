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
sonosctl search "test" --speaker "Living Room"
```

If both commands succeed, operations are ready.

## 2) Core commands during shift

Play a track (with interactive selection):

```bash
sonosctl play "track name" --speaker "Living Room" --pick
```

Search without playing:

```bash
sonosctl search "track name" --speaker "Living Room"
```

Check current playback before transitions:

```bash
sonosctl status --speaker "Living Room"
```

Transport and volume:

```bash
sonosctl pause --speaker "Living Room"
sonosctl resume --speaker "Living Room"
sonosctl next --speaker "Living Room"
sonosctl prev --speaker "Living Room"
sonosctl volume 35 --speaker "Living Room"
```

View playlists:

```bash
sonosctl playlists --speaker "Living Room"
sonosctl playlists chill --speaker "Living Room"
```

## 3) Multi-speaker operation

Group `Office` into `Living Room`:

```bash
sonosctl group --coordinator "Living Room" --members "Office"
```

Play on coordinator (audio in both rooms):

```bash
sonosctl play "track name" --speaker "Living Room" --pick
```

Ungroup:

```bash
sonosctl ungroup --speaker "Office"
```

## 4) Shift end checklist

1. Set agreed volume level (example 25-35):

```bash
sonosctl volume 30 --speaker "Living Room"
```

2. Pause playback or set closing playlist per policy:

```bash
sonosctl pause --speaker "Living Room"
```

3. If temporary grouping was used, ungroup speakers:

```bash
sonosctl ungroup --speaker "Office"
```

## 5) Common incidents and quick fixes

### A) `AuthTokenExpired`

Re-authorize:

```bash
sonosctl auth-spotify --speaker "Living Room"
sonosctl search "test" --speaker "Living Room"
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
sonosctl group --coordinator "Living Room" --members "Office"
```

## 6) Operational rules

1. One active operator per shift.
2. Always use exact speaker names from `sonosctl devices`.
3. Use `Living Room` as standard multi-room coordinator.
4. If an issue persists, capture command + full error and escalate.

## 7) Quick reference

```bash
sonosctl devices
sonosctl play "daft punk one more time" --speaker "Living Room" --pick
sonosctl group --coordinator "Living Room" --members "Office"
sonosctl ungroup --speaker "Office"
sonosctl auth-spotify --speaker "Living Room"
```

Queue management during shifts:

```bash
sonosctl queue --speaker "Living Room"
sonosctl queue add "track name" --speaker "Living Room"
```

Playlist mode during shifts:

```bash
sonosctl play-playlist "Chill Vibes" --speaker "Living Room" --shuffle
```

Playback mode controls during shifts:

```bash
sonosctl shuffle on --speaker "Living Room"
sonosctl repeat all --speaker "Living Room"
sonosctl crossfade on --speaker "Living Room"
```

