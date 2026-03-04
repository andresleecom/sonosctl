from __future__ import annotations

import argparse
import json

from sonosctl.config import (
    DEFAULT_SEARCH_LIMIT,
    effective_ip,
    effective_json_flag,
    effective_search_limit,
    effective_speaker,
    effective_timeout,
)
from sonosctl.speaker import resolve_speaker
from sonosctl.spotify import list_playlists, search_tracks


def cmd_search(args: argparse.Namespace) -> int:
    speaker = None
    speaker_name = effective_speaker(args)
    speaker_ip = effective_ip(args)
    if speaker_name or speaker_ip:
        speaker = resolve_speaker(
            name=speaker_name,
            ip=speaker_ip,
            timeout=effective_timeout(args),
        )

    limit = effective_search_limit(args, DEFAULT_SEARCH_LIMIT)
    tracks = search_tracks(term=args.query, limit=limit, device=speaker)
    if not tracks:
        if effective_json_flag(args):
            print(json.dumps({"tracks": []}, indent=2))
        else:
            print("No tracks found.")
        return 0

    if effective_json_flag(args):
        payload = {
            "tracks": [
                {
                    "index": idx,
                    "title": track.title,
                    "artist": track.artist,
                    "album": track.album,
                }
                for idx, track in enumerate(tracks, start=1)
            ]
        }
        print(json.dumps(payload, indent=2))
        return 0

    for idx, track in enumerate(tracks, start=1):
        print(f"{idx}. {track.title} - {track.artist} ({track.album})")
    return 0


def cmd_playlists(args: argparse.Namespace) -> int:
    speaker = None
    speaker_name = effective_speaker(args)
    speaker_ip = effective_ip(args)
    if speaker_name or speaker_ip:
        speaker = resolve_speaker(
            name=speaker_name,
            ip=speaker_ip,
            timeout=effective_timeout(args),
        )

    limit = effective_search_limit(args, DEFAULT_SEARCH_LIMIT)
    playlists = list_playlists(limit=limit, query=args.query or "", device=speaker)
    if not playlists:
        if effective_json_flag(args):
            print(json.dumps({"playlists": []}, indent=2))
        else:
            print("No playlists found.")
        return 0

    if effective_json_flag(args):
        payload = {
            "playlists": [
                {
                    "index": idx,
                    "title": playlist.title,
                    "owner": playlist.owner,
                    "id": playlist.item_id,
                }
                for idx, playlist in enumerate(playlists, start=1)
            ]
        }
        print(json.dumps(payload, indent=2))
        return 0

    for idx, playlist in enumerate(playlists, start=1):
        print(f"{idx}. {playlist.title} - {playlist.owner}")
    return 0
