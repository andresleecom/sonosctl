from __future__ import annotations

import argparse
import json

from sonosctl.config import effective_json_flag, effective_speaker
from sonosctl.history import history_path, read_playback_history


def cmd_history(args: argparse.Namespace) -> int:
    speaker = effective_speaker(args)
    entries = read_playback_history(limit=max(1, args.limit), speaker=speaker)

    if effective_json_flag(args):
        payload = {
            "path": str(history_path()),
            "speaker": speaker,
            "count": len(entries),
            "entries": [
                {
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
                for entry in entries
            ],
        }
        print(json.dumps(payload, indent=2))
        return 0

    if not entries:
        target = f" for {speaker}" if speaker else ""
        print(f"No playback history found{target}.")
        print(f"History file: {history_path()}")
        return 0

    print(f"Playback history: {history_path()}")
    for idx, entry in enumerate(entries, start=1):
        details = f"{entry.track} - {entry.artist}"
        if entry.album != "Unknown":
            details += f" ({entry.album})"
        print(f"{idx}. [{entry.observed_at}] {entry.speaker}: {details}")
    return 0
