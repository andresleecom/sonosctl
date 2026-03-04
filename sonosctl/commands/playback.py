from __future__ import annotations

import argparse
import json
from typing import Sequence

from sonosctl.config import (
    DEFAULT_PLAY_NON_PICK_LIMIT,
    DEFAULT_PLAY_PICK_LIMIT,
    effective_ip,
    effective_json_flag,
    effective_replace_queue,
    effective_search_limit,
    effective_speaker,
    effective_timeout,
)
from sonosctl.speaker import resolve_speaker, with_speaker
from sonosctl.spotify import search_tracks
from sonosctl.types import TrackResult


def prompt_track_selection(tracks: Sequence[TrackResult]) -> TrackResult | None:
    for idx, track in enumerate(tracks, start=1):
        print(f"{idx}. {track.title} - {track.artist} ({track.album})")

    while True:
        choice = input(f"Pick track [1-{len(tracks)}], or 'q' to cancel: ").strip().lower()
        if choice in {"q", "quit", "exit"}:
            return None
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(tracks):
                return tracks[index - 1]
        print("Invalid choice.")


def cmd_play(args: argparse.Namespace) -> int:
    speaker = resolve_speaker(
        name=effective_speaker(args),
        ip=effective_ip(args),
        timeout=effective_timeout(args),
    )
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

    if effective_replace_queue(args):
        speaker.clear_queue()

    queue_position = speaker.add_to_queue(track.item)
    speaker.play_from_queue(queue_position - 1)

    print(
        f"Now playing on {speaker.player_name}: {track.title} - {track.artist}"
    )
    return 0


def cmd_pause(args: argparse.Namespace) -> int:
    speaker = with_speaker(args, "pause")
    speaker.pause()
    print(f"Paused {speaker.player_name}")
    return 0


def cmd_resume(args: argparse.Namespace) -> int:
    speaker = with_speaker(args, "resume")
    speaker.play()
    print(f"Resumed {speaker.player_name}")
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    speaker = with_speaker(args, "skip")
    speaker.next()
    print(f"Skipped track on {speaker.player_name}")
    return 0


def cmd_prev(args: argparse.Namespace) -> int:
    speaker = with_speaker(args, "go to previous")
    speaker.previous()
    print(f"Went to previous track on {speaker.player_name}")
    return 0


def cmd_volume(args: argparse.Namespace) -> int:
    speaker = with_speaker(args, "set volume")
    if args.level is None:
        print(f"{speaker.player_name} volume: {speaker.volume}")
        return 0

    if args.level < 0 or args.level > 100:
        print("Volume must be between 0 and 100.")
        return 1

    speaker.volume = args.level
    print(f"{speaker.player_name} volume set to {args.level}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    speaker = with_speaker(args, "get status")
    transport = speaker.get_current_transport_info()
    track = speaker.get_current_track_info()
    media = speaker.get_current_media_info()

    state = str(transport.get("current_transport_state", "UNKNOWN")).upper()
    title = track.get("title") or "Unknown"
    artist = track.get("artist") or "Unknown"
    album = track.get("album") or "Unknown"
    position = track.get("position") or "0:00:00"
    duration = track.get("duration") or "0:00:00"
    volume = int(speaker.volume)
    source = media.get("channel") or media.get("uri") or "Unknown"

    if effective_json_flag(args):
        payload = {
            "speaker": speaker.player_name or speaker.ip_address,
            "state": state,
            "track": title,
            "artist": artist,
            "album": album,
            "position": position,
            "duration": duration,
            "volume": volume,
            "source": source,
        }
        print(json.dumps(payload, indent=2))
        return 0

    print(f"Speaker: {speaker.player_name}")
    print(f"State: {state}")
    print(f"Track: {title}")
    print(f"Artist: {artist}")
    print(f"Album: {album}")
    print(f"Position: {position} / {duration}")
    print(f"Volume: {volume}")
    print(f"Source: {source}")
    return 0
