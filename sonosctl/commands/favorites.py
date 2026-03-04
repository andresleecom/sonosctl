from __future__ import annotations

import argparse
import json

from sonosctl.config import effective_json_flag
from sonosctl.speaker import with_speaker
from sonosctl.spotify import list_favorites


def cmd_favorites(args: argparse.Namespace) -> int:
    speaker = with_speaker(args, "list favorites")
    favorites = list_favorites(
        speaker=speaker,
        limit=max(1, args.limit),
        offset=max(0, args.offset),
        kind_filter=args.kind,
        query=args.query or "",
    )

    if effective_json_flag(args):
        payload = {
            "speaker": speaker.player_name or speaker.ip_address,
            "kind": args.kind,
            "offset": max(0, args.offset),
            "limit": max(1, args.limit),
            "favorites": [
                {
                    "index": idx,
                    "title": fav.title,
                    "kind": fav.kind,
                    "id": fav.item_id,
                    "uri": fav.uri,
                }
                for idx, fav in enumerate(favorites, start=1)
            ],
        }
        print(json.dumps(payload, indent=2))
        return 0

    if not favorites:
        print("No favorites found.")
        return 0

    print(f"Favorites on {speaker.player_name} ({args.kind}):")
    for idx, fav in enumerate(favorites, start=1):
        print(f"{idx}. {fav.title} [{fav.kind}]")
    return 0
