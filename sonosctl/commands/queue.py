from __future__ import annotations

import argparse
import json

from sonosctl.config import (
    DEFAULT_PLAY_NON_PICK_LIMIT,
    DEFAULT_PLAY_PICK_LIMIT,
    effective_json_flag,
    effective_search_limit,
)
from sonosctl.commands.playback import prompt_track_selection
from sonosctl.speaker import with_speaker
from sonosctl.spotify import _safe_getattr, search_tracks, track_artist_album


def cmd_queue_list(args: argparse.Namespace) -> int:
    speaker = with_speaker(args, "read queue")
    queue_items = speaker.get_queue(start=args.offset, max_items=args.limit)
    current_track = speaker.get_current_track_info()
    current_position = current_track.get("playlist_position")

    rows = []
    for idx, item in enumerate(queue_items, start=args.offset + 1):
        artist, album = track_artist_album(item)
        rows.append(
            {
                "position": idx,
                "title": _safe_getattr(item, "title", "Unknown"),
                "artist": artist,
                "album": album,
                "id": _safe_getattr(item, "item_id", ""),
            }
        )

    if effective_json_flag(args):
        payload = {
            "speaker": speaker.player_name or speaker.ip_address,
            "offset": args.offset,
            "limit": args.limit,
            "current_queue_position": current_position,
            "items": rows,
        }
        print(json.dumps(payload, indent=2))
        return 0

    if not rows:
        print(f"Queue is empty on {speaker.player_name}.")
        return 0

    print(f"Queue on {speaker.player_name}:")
    for row in rows:
        marker = ""
        if current_position and str(row["position"]) == str(current_position):
            marker = " >"
        print(f'{row["position"]}. {row["title"]} - {row["artist"]} ({row["album"]}){marker}')
    return 0


def cmd_queue_add(args: argparse.Namespace) -> int:
    speaker = with_speaker(args, "add to queue")
    search_limit = effective_search_limit(
        args, DEFAULT_PLAY_PICK_LIMIT if args.pick else DEFAULT_PLAY_NON_PICK_LIMIT
    )
    tracks = search_tracks(term=args.query, limit=search_limit, device=speaker)
    if not tracks:
        print(f"No Spotify track found for query: {args.query}")
        return 1

    track = tracks[0]
    if args.pick:
        selected = prompt_track_selection(tracks)
        if selected is None:
            print("Canceled.")
            return 0
        track = selected

    queue_position = speaker.add_to_queue(track.item)
    print(
        f"Added to queue on {speaker.player_name}: {track.title} - {track.artist} (position {queue_position})"
    )
    return 0


def cmd_queue_clear(args: argparse.Namespace) -> int:
    speaker = with_speaker(args, "clear queue")
    speaker.clear_queue()
    print(f"Queue cleared on {speaker.player_name}")
    return 0
