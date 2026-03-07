from __future__ import annotations

import argparse
import json
import time

from sonosctl.commands.playback import playback_snapshot, record_snapshot_history
from sonosctl.config import effective_json_flag
from sonosctl.history import PlaybackHistoryEntry
from sonosctl.speaker import with_speaker


def _entry_payload(entry: PlaybackHistoryEntry) -> dict:
    return {
        "observed_at": entry.observed_at,
        "speaker": entry.speaker,
        "track": entry.track,
        "artist": entry.artist,
        "album": entry.album,
        "source": entry.source,
        "state": entry.state,
        "duration": entry.duration,
        "position": entry.position,
        "group_coordinator": entry.group_coordinator,
    }


def cmd_monitor(args: argparse.Namespace) -> int:
    speaker = with_speaker(args, "monitor playback")
    interval = max(1.0, float(args.interval))
    iteration = 0

    while True:
        payload, _, _, _ = playback_snapshot(speaker)
        entry = record_snapshot_history(payload)

        if entry:
            if effective_json_flag(args):
                print(json.dumps(_entry_payload(entry), indent=2))
            else:
                details = f"{entry.track} - {entry.artist}"
                if entry.album != "Unknown":
                    details += f" ({entry.album})"
                print(f"[{entry.observed_at}] {entry.speaker}: {details}")
        elif iteration == 0 and not effective_json_flag(args):
            print(
                f"Monitoring {payload['speaker']} every {interval:.0f}s. "
                "New PLAYING tracks will be appended to history."
            )

        iteration += 1
        time.sleep(interval)
