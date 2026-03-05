from __future__ import annotations

import argparse
import sys
from typing import Iterable

from sonosctl.commands import (
    cmd_auth_spotify,
    cmd_crossfade,
    cmd_doctor_status,
    cmd_devices,
    cmd_favorites,
    cmd_group,
    cmd_groups,
    cmd_next,
    cmd_pause,
    cmd_play,
    cmd_play_playlist,
    cmd_playlists,
    cmd_prev,
    cmd_queue_add,
    cmd_queue_clear,
    cmd_queue_list,
    cmd_repeat,
    cmd_resume,
    cmd_search,
    cmd_shuffle,
    cmd_status,
    cmd_ungroup,
    cmd_volume,
)
from sonosctl.config import default_config_path, load_config


def add_speaker_selection_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--speaker", default=None, help="Sonos speaker name (e.g. 'Living Room')")
    parser.add_argument("--ip", default=None, help="Direct Sonos speaker IP (overrides --speaker)")
    parser.add_argument("--timeout", type=int, default=None, help="Discovery timeout in seconds")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sonosctl",
        description="Control Sonos speakers and Spotify playback from CLI.",
    )
    parser.add_argument(
        "--config",
        default=None,
        help=f"Path to config file (default: {default_config_path()})",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    devices = subparsers.add_parser("devices", help="List Sonos speakers on your LAN")
    devices.add_argument("--timeout", type=int, default=None, help="Discovery timeout in seconds")
    devices.add_argument(
        "--json",
        action="store_true",
        default=None,
        help="Output JSON",
    )
    devices.set_defaults(func=cmd_devices)

    search = subparsers.add_parser("search", help="Search Spotify tracks")
    search.add_argument("query", help="Search query, e.g. 'Daft Punk One More Time'")
    search.add_argument("--limit", type=int, default=None, help="Max results")
    add_speaker_selection_args(search)
    search.add_argument(
        "--json",
        action="store_true",
        default=None,
        help="Output JSON",
    )
    search.set_defaults(func=cmd_search)

    playlists = subparsers.add_parser("playlists", help="List Spotify playlists")
    playlists.add_argument("query", nargs="?", default=None, help="Optional filter query")
    playlists.add_argument("--limit", type=int, default=None, help="Max results")
    add_speaker_selection_args(playlists)
    playlists.add_argument(
        "--json",
        action="store_true",
        default=None,
        help="Output JSON",
    )
    playlists.set_defaults(func=cmd_playlists)

    favorites = subparsers.add_parser("favorites", help="List Sonos favorites")
    favorites.add_argument(
        "kind",
        nargs="?",
        default="all",
        choices=["all", "playlists", "tracks"],
        help="Filter favorites by type",
    )
    favorites.add_argument("query", nargs="?", default=None, help="Optional filter query")
    favorites.add_argument("--limit", type=int, default=50, help="Max favorites to show")
    favorites.add_argument("--offset", type=int, default=0, help="Favorites offset")
    add_speaker_selection_args(favorites)
    favorites.add_argument(
        "--json",
        action="store_true",
        default=None,
        help="Output JSON",
    )
    favorites.set_defaults(func=cmd_favorites)

    play = subparsers.add_parser("play", help="Search and play first Spotify match")
    play.add_argument("query", help="Track search query")
    play.add_argument(
        "--replace-queue",
        action="store_true",
        default=None,
        help="Clear queue before adding track",
    )
    play.add_argument("--pick", action="store_true", help="Interactively pick from search results")
    play.add_argument("--limit", type=int, default=None, help="Search result count (used by --pick)")
    add_speaker_selection_args(play)
    play.set_defaults(func=cmd_play)

    play_playlist = subparsers.add_parser("play-playlist", help="Play a Spotify playlist by name or ID")
    play_playlist.add_argument("selector", help="Playlist name or playlist item ID")
    play_playlist.add_argument("--limit", type=int, default=20, help="Search result count for lookup")
    play_playlist.add_argument("--shuffle", action="store_true", help="Enable shuffle before playback")
    play_playlist.add_argument(
        "--keep-queue",
        action="store_true",
        help="Do not clear queue before adding playlist (default is to clear queue)",
    )
    add_speaker_selection_args(play_playlist)
    play_playlist.set_defaults(func=cmd_play_playlist)

    shuffle = subparsers.add_parser("shuffle", help="Show or set shuffle mode")
    shuffle.add_argument("mode", nargs="?", choices=["on", "off"], help="Shuffle mode")
    add_speaker_selection_args(shuffle)
    shuffle.add_argument(
        "--json",
        action="store_true",
        default=None,
        help="Output JSON",
    )
    shuffle.set_defaults(func=cmd_shuffle)

    repeat = subparsers.add_parser("repeat", help="Show or set repeat mode")
    repeat.add_argument("mode", nargs="?", choices=["off", "all", "one"], help="Repeat mode")
    add_speaker_selection_args(repeat)
    repeat.add_argument(
        "--json",
        action="store_true",
        default=None,
        help="Output JSON",
    )
    repeat.set_defaults(func=cmd_repeat)

    crossfade = subparsers.add_parser("crossfade", help="Show or set crossfade mode")
    crossfade.add_argument("mode", nargs="?", choices=["on", "off"], help="Crossfade mode")
    add_speaker_selection_args(crossfade)
    crossfade.add_argument(
        "--json",
        action="store_true",
        default=None,
        help="Output JSON",
    )
    crossfade.set_defaults(func=cmd_crossfade)

    queue = subparsers.add_parser("queue", help="View and manage playback queue")
    queue.add_argument("--limit", type=int, default=20, help="Max queue items to show")
    queue.add_argument("--offset", type=int, default=0, help="Queue offset")
    add_speaker_selection_args(queue)
    queue.add_argument(
        "--json",
        action="store_true",
        default=None,
        help="Output JSON",
    )
    queue_subparsers = queue.add_subparsers(dest="queue_command")
    queue.set_defaults(func=cmd_queue_list)

    queue_add = queue_subparsers.add_parser("add", help="Search and add a track to queue")
    queue_add.add_argument("query", help="Track search query")
    queue_add.add_argument("--limit", type=int, default=None, help="Search result count (used by --pick)")
    queue_add.add_argument("--pick", action="store_true", help="Interactively pick from search results")
    add_speaker_selection_args(queue_add)
    queue_add.set_defaults(func=cmd_queue_add)

    queue_clear = queue_subparsers.add_parser("clear", help="Clear current playback queue")
    add_speaker_selection_args(queue_clear)
    queue_clear.set_defaults(func=cmd_queue_clear)

    status = subparsers.add_parser("status", help="Show current playback status")
    add_speaker_selection_args(status)
    status.add_argument(
        "--json",
        action="store_true",
        default=None,
        help="Output JSON",
    )
    status.add_argument(
        "--raw",
        action="store_true",
        help="Include raw Sonos response payloads (debug)",
    )
    status.set_defaults(func=cmd_status)

    group = subparsers.add_parser("group", help="Group speakers under a coordinator")
    group.add_argument("--coordinator", required=True, help="Coordinator speaker name")
    group.add_argument(
        "--members",
        nargs="+",
        required=True,
        help="Speaker names to join the coordinator group",
    )
    group.add_argument("--wait", type=float, default=2.0, help="Seconds to wait for group confirmation")
    group.add_argument("--timeout", type=int, default=None, help="Discovery timeout in seconds")
    group.set_defaults(func=cmd_group)

    ungroup = subparsers.add_parser("ungroup", help="Remove a speaker from its group")
    add_speaker_selection_args(ungroup)
    ungroup.add_argument("--wait", type=float, default=2.0, help="Seconds to wait for ungroup confirmation")
    ungroup.set_defaults(func=cmd_ungroup)

    groups = subparsers.add_parser("groups", help="Show current Sonos group topology")
    groups.add_argument("--timeout", type=int, default=None, help="Discovery timeout in seconds")
    groups.add_argument("--json", action="store_true", default=None, help="Output JSON")
    groups.set_defaults(func=cmd_groups)

    doctor = subparsers.add_parser("doctor", help="Diagnostics tools")
    doctor_subparsers = doctor.add_subparsers(dest="doctor_command", required=True)

    doctor_status = doctor_subparsers.add_parser("status", help="Analyze captured status --json --raw output")
    doctor_status.add_argument(
        "--input",
        default="status-debug.jsonl",
        help="Path to captured status file (concatenated JSON documents)",
    )
    doctor_status.add_argument("--samples", type=int, default=5, help="How many Unknown samples to print")
    doctor_status.set_defaults(func=cmd_doctor_status)

    auth = subparsers.add_parser("auth-spotify", help="Run one-time Spotify auth for this CLI")
    add_speaker_selection_args(auth)
    auth.set_defaults(func=cmd_auth_spotify)

    pause = subparsers.add_parser("pause", help="Pause playback")
    add_speaker_selection_args(pause)
    pause.set_defaults(func=cmd_pause)

    resume = subparsers.add_parser("resume", help="Resume playback")
    add_speaker_selection_args(resume)
    resume.set_defaults(func=cmd_resume)

    nxt = subparsers.add_parser("next", help="Skip to next track")
    add_speaker_selection_args(nxt)
    nxt.set_defaults(func=cmd_next)

    prv = subparsers.add_parser("prev", help="Go to previous track")
    add_speaker_selection_args(prv)
    prv.set_defaults(func=cmd_prev)

    volume = subparsers.add_parser("volume", help="Get or set speaker volume")
    volume.add_argument("level", type=int, nargs="?", help="0-100")
    add_speaker_selection_args(volume)
    volume.set_defaults(func=cmd_volume)

    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    args.config_defaults = load_config(args.config).defaults

    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("Interrupted.")
        return 130
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
