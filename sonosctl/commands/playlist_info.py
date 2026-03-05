from __future__ import annotations

import argparse
import json

from sonosctl.speaker import with_speaker
from sonosctl.spotify import get_playlist_tracks, list_playlists
from sonosctl.commands.playlist import _select_playlist


def _format_duration(seconds: int) -> str:
    if seconds <= 0:
        return "0:00"
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m:02d}m"
    return f"{m}:{s:02d}"


def _format_track_duration(seconds: int) -> str:
    if seconds <= 0:
        return "0:00"
    m, s = divmod(seconds, 60)
    return f"{m}:{s:02d}"


def cmd_playlist_info(args: argparse.Namespace) -> int:
    speaker = with_speaker(args, "playlist info")
    search_limit = max(1, args.limit)

    playlists = list_playlists(limit=search_limit, query=args.selector, device=speaker)
    selected = _select_playlist(playlists, args.selector)
    if selected is None:
        expanded = list_playlists(limit=max(100, search_limit), query="", device=speaker)
        selected = _select_playlist(expanded, args.selector)

    if selected is None:
        print(f"No playlist found for selector: {args.selector}")
        return 1

    tracks = get_playlist_tracks(selected.item_id, device=speaker)
    total_seconds = sum(t["duration_seconds"] for t in tracks)

    if getattr(args, "json", None):
        print(json.dumps({
            "playlist": selected.title,
            "owner": selected.owner,
            "track_count": len(tracks),
            "total_duration_seconds": total_seconds,
            "total_duration": _format_duration(total_seconds),
            "tracks": tracks,
        }, indent=2))
        return 0

    print(f"Playlist: {selected.title} (by {selected.owner})")
    print(f"Tracks: {len(tracks)} | Duration: {_format_duration(total_seconds)}")
    print()

    if not tracks:
        print("  (empty playlist)")
        return 0

    max_title = max(len(t["title"]) for t in tracks)
    max_artist = max(len(t["artist"]) for t in tracks)
    max_title = min(max(max_title, 5), 40)
    max_artist = min(max(max_artist, 6), 25)

    header = f"  {'#':>3}  {'Track':<{max_title}}  {'Artist':<{max_artist}}  Duration"
    print(header)
    for i, t in enumerate(tracks, 1):
        title = t["title"][:max_title]
        artist = t["artist"][:max_artist]
        dur = _format_track_duration(t["duration_seconds"])
        print(f"  {i:>3}  {title:<{max_title}}  {artist:<{max_artist}}  {dur:>7}")

    return 0
