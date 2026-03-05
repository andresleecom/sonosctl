from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def _parse_json_stream(text: str) -> list[dict]:
    decoder = json.JSONDecoder()
    idx = 0
    n = len(text)
    docs: list[dict] = []
    while idx < n:
        while idx < n and text[idx].isspace():
            idx += 1
        if idx >= n:
            break
        obj, next_idx = decoder.raw_decode(text, idx)
        if isinstance(obj, dict):
            docs.append(obj)
        idx = next_idx
    return docs


def cmd_doctor_status(args: argparse.Namespace) -> int:
    path = Path(args.input)
    if not path.exists():
        print(f"Input file not found: {path}")
        return 1

    text = path.read_text(encoding="utf-8", errors="replace")
    docs = _parse_json_stream(text)
    if not docs:
        print("No JSON status records found in input.")
        return 1

    total = len(docs)
    unknown_track = 0
    unknown_artist = 0
    unknown_album = 0
    unknown_any = 0
    states = Counter()
    sources = Counter()
    unknown_samples: list[dict] = []

    for doc in docs:
        track = str(doc.get("track", "Unknown"))
        artist = str(doc.get("artist", "Unknown"))
        album = str(doc.get("album", "Unknown"))
        state = str(doc.get("state", "UNKNOWN"))
        source = str(doc.get("source", "Unknown"))

        states[state] += 1
        sources[source] += 1

        is_track_unknown = track == "Unknown"
        is_artist_unknown = artist == "Unknown"
        is_album_unknown = album == "Unknown"
        if is_track_unknown:
            unknown_track += 1
        if is_artist_unknown:
            unknown_artist += 1
        if is_album_unknown:
            unknown_album += 1
        if is_track_unknown or is_artist_unknown or is_album_unknown:
            unknown_any += 1
            if len(unknown_samples) < max(0, args.samples):
                unknown_samples.append(
                    {
                        "state": state,
                        "track": track,
                        "artist": artist,
                        "album": album,
                        "source": source,
                    }
                )

    print("Status Diagnostics")
    print(f"Input: {path}")
    print(f"Records: {total}")
    print(
        "Unknown rates: "
        f"track={unknown_track}/{total} "
        f"artist={unknown_artist}/{total} "
        f"album={unknown_album}/{total} "
        f"any={unknown_any}/{total}"
    )

    print("Top states:")
    for state, count in states.most_common(5):
        print(f"- {state}: {count}")

    print("Top sources:")
    for source, count in sources.most_common(5):
        print(f"- {source}: {count}")

    if unknown_samples:
        print("Unknown samples:")
        for i, sample in enumerate(unknown_samples, start=1):
            print(f"{i}. {json.dumps(sample, ensure_ascii=True)}")

    if unknown_any == 0:
        print("No Unknown fields detected in this capture.")
    elif states.get("PLAYING", 0) > 0 and unknown_any / total > 0.2:
        print("High Unknown rate while PLAYING. Check raw payload consistency and source metadata.")
    else:
        print("Unknown values detected; compare with source/state distribution above.")

    return 0
