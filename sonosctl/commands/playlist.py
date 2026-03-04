from __future__ import annotations

import argparse
from typing import Sequence

from sonosctl.speaker import with_speaker
from sonosctl.spotify import list_playlists
from sonosctl.types import PlaylistResult


def _select_playlist(playlists: Sequence[PlaylistResult], selector: str) -> PlaylistResult | None:
    normalized = selector.strip().lower()
    if not normalized:
        return None

    by_id = [p for p in playlists if p.item_id.lower() == normalized]
    if by_id:
        return by_id[0]

    exact_title = [p for p in playlists if p.title.lower() == normalized]
    if exact_title:
        return exact_title[0]

    partial_title = [p for p in playlists if normalized in p.title.lower()]
    if partial_title:
        return partial_title[0]

    return None


def cmd_play_playlist(args: argparse.Namespace) -> int:
    speaker = with_speaker(args, "play playlist")
    search_limit = max(1, args.limit)

    playlists = list_playlists(limit=search_limit, query=args.selector, device=speaker)
    selected = _select_playlist(playlists, args.selector)
    if selected is None:
        expanded = list_playlists(limit=max(100, search_limit), query="", device=speaker)
        selected = _select_playlist(expanded, args.selector)

    if selected is None:
        print(f"No playlist found for selector: {args.selector}")
        return 1

    replace_queue = not args.keep_queue
    if replace_queue:
        speaker.clear_queue()

    if args.shuffle:
        speaker.shuffle = True

    queue_position = speaker.add_to_queue(selected.item)
    speaker.play_from_queue(max(0, queue_position - 1))

    action = "replaced queue and started" if replace_queue else "queued and started"
    print(
        f'Now playing playlist on {speaker.player_name}: "{selected.title}" ({selected.owner}) [{action}]'
    )
    return 0
