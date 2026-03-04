#!/usr/bin/env python3
"""Control Sonos speakers and Spotify playback from the command line.

This CLI uses the Spotify account linked in your Sonos app.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Iterable, Sequence
from urllib.parse import parse_qs, urlparse

import soco
from soco import SoCo
from soco.music_services import MusicService

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - python < 3.11
    import tomli as tomllib


DEFAULT_TIMEOUT = 5
DEFAULT_SEARCH_LIMIT = 5
DEFAULT_PLAY_PICK_LIMIT = 10
DEFAULT_PLAY_NON_PICK_LIMIT = 1


@dataclass
class TrackResult:
    title: str
    artist: str
    album: str
    item: object


@dataclass
class PlaylistResult:
    title: str
    owner: str
    item_id: str
    item: object


@dataclass
class ConfigDefaults:
    speaker: str | None = None
    ip: str | None = None
    timeout: int | None = None
    search_limit: int | None = None
    json_output: bool | None = None
    replace_queue: bool | None = None


@dataclass
class AppConfig:
    defaults: ConfigDefaults


def default_config_path() -> str:
    return os.path.join(os.path.expanduser("~"), ".sonosctl", "config.toml")


def load_config(path: str | None) -> AppConfig:
    config_path = path or default_config_path()
    if not os.path.exists(config_path):
        return AppConfig(defaults=ConfigDefaults())

    with open(config_path, "rb") as fp:
        data = tomllib.load(fp)

    defaults = data.get("defaults", {})
    return AppConfig(
        defaults=ConfigDefaults(
            speaker=_opt_str(defaults.get("speaker")),
            ip=_opt_str(defaults.get("ip")),
            timeout=_opt_int(defaults.get("timeout")),
            search_limit=_opt_int(defaults.get("search_limit")),
            json_output=_opt_bool(defaults.get("json")),
            replace_queue=_opt_bool(defaults.get("replace_queue")),
        )
    )


def _opt_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def _opt_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _opt_bool(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
    return None


def effective_timeout(args: argparse.Namespace) -> int:
    value = args.timeout if args.timeout is not None else args.config_defaults.timeout
    return value if value is not None else DEFAULT_TIMEOUT


def effective_speaker(args: argparse.Namespace) -> str | None:
    return args.speaker if args.speaker is not None else args.config_defaults.speaker


def effective_ip(args: argparse.Namespace) -> str | None:
    return args.ip if args.ip is not None else args.config_defaults.ip


def effective_search_limit(args: argparse.Namespace, fallback: int) -> int:
    value = args.limit if args.limit is not None else args.config_defaults.search_limit
    if value is None:
        return fallback
    return max(1, value)


def effective_json_flag(args: argparse.Namespace) -> bool:
    if args.json is not None:
        return args.json
    if args.config_defaults.json_output is not None:
        return args.config_defaults.json_output
    return False


def effective_replace_queue(args: argparse.Namespace) -> bool:
    if args.replace_queue is not None:
        return args.replace_queue
    if args.config_defaults.replace_queue is not None:
        return args.config_defaults.replace_queue
    return False


def discover_speakers(timeout: int = DEFAULT_TIMEOUT) -> list[SoCo]:
    devices = soco.discover(timeout=timeout)
    if not devices:
        return []
    return sorted(devices, key=lambda d: (d.player_name or "").lower())


def print_speakers(devices: Sequence[SoCo]) -> None:
    if not devices:
        print("No Sonos speakers found on your network.")
        return

    for speaker in devices:
        name = speaker.player_name or "Unknown"
        model = getattr(speaker, "model_name", "Unknown")
        print(f"{name} | {speaker.ip_address} | {model}")


def resolve_speaker(name: str | None, ip: str | None, timeout: int = DEFAULT_TIMEOUT) -> SoCo:
    if ip:
        return SoCo(ip)

    devices = discover_speakers(timeout=timeout)
    if not devices:
        raise RuntimeError("No Sonos speakers discovered. Ensure your speaker is online and on same LAN.")

    if name:
        exact = [d for d in devices if (d.player_name or "").lower() == name.lower()]
        if len(exact) == 1:
            return exact[0]

        partial = [d for d in devices if name.lower() in (d.player_name or "").lower()]
        if len(partial) == 1:
            return partial[0]

        available = ", ".join((d.player_name or d.ip_address) for d in devices)
        raise RuntimeError(f"Could not uniquely match speaker '{name}'. Available: {available}")

    if len(devices) == 1:
        return devices[0]

    available = ", ".join((d.player_name or d.ip_address) for d in devices)
    raise RuntimeError(f"Multiple speakers found. Pass --speaker or --ip. Available: {available}")


def spotify_service(device: SoCo | None = None) -> MusicService:
    try:
        return MusicService("Spotify", device=device)
    except Exception as exc:  # pragma: no cover - depends on live environment
        raise RuntimeError(
            "Spotify service not available from Sonos. Link Spotify in the Sonos app first."
        ) from exc


def _safe_getattr(obj: object, attr: str, fallback: str = "") -> str:
    value = getattr(obj, attr, fallback)
    if value is None:
        return fallback
    return str(value)


def search_tracks(term: str, limit: int = DEFAULT_SEARCH_LIMIT, device: SoCo | None = None) -> list[TrackResult]:
    service = spotify_service(device=device)
    results = service.search(category="tracks", term=term, count=limit)

    items: list[TrackResult] = []
    for item in results:
        title = _safe_getattr(item, "title", "Unknown")

        artist = "Unknown"
        album = "Unknown"

        metadata = getattr(item, "metadata", None)
        if metadata:
            artist = _safe_getattr(metadata, "artist", artist)
            album = _safe_getattr(metadata, "album", album)

        items.append(TrackResult(title=title, artist=artist, album=album, item=item))

    return items


def _playlist_owner_from_item(item: object) -> str:
    metadata = getattr(item, "metadata", None)
    if metadata:
        owner = _safe_getattr(metadata, "artist", "")
        if owner:
            return owner
        owner = _safe_getattr(metadata, "creator", "")
        if owner:
            return owner
    return "Unknown"


def list_playlists(
    limit: int = DEFAULT_SEARCH_LIMIT,
    query: str = "",
    device: SoCo | None = None,
) -> list[PlaylistResult]:
    service = spotify_service(device=device)
    items: list[PlaylistResult] = []

    try:
        if "playlists" in service.available_search_categories:
            result = service.search(category="playlists", term=query, count=limit)
            for item in result:
                items.append(
                    PlaylistResult(
                        title=_safe_getattr(item, "title", "Unknown"),
                        owner=_playlist_owner_from_item(item),
                        item_id=_safe_getattr(item, "id", ""),
                        item=item,
                    )
                )
    except Exception:
        pass

    if items:
        return items[:limit]

    try:
        search_prefix = service._get_search_prefix_map().get("playlists")  # pylint: disable=protected-access
        if search_prefix:
            result = service.get_metadata(item=search_prefix, count=limit)
            for item in result:
                items.append(
                    PlaylistResult(
                        title=_safe_getattr(item, "title", "Unknown"),
                        owner=_playlist_owner_from_item(item),
                        item_id=_safe_getattr(item, "id", ""),
                        item=item,
                    )
                )
    except Exception:
        pass

    if query:
        q = query.lower()
        items = [x for x in items if q in x.title.lower() or q in x.owner.lower() or q in x.item_id.lower()]

    return items[:limit]


def cmd_devices(args: argparse.Namespace) -> int:
    devices = discover_speakers(timeout=effective_timeout(args))
    if effective_json_flag(args):
        payload = {
            "speakers": [
                {
                    "name": speaker.player_name or "Unknown",
                    "ip": speaker.ip_address,
                    "model": getattr(speaker, "model_name", "Unknown"),
                }
                for speaker in devices
            ]
        }
        print(json.dumps(payload, indent=2))
        return 0

    print_speakers(devices)
    return 0


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


def _with_speaker(args: argparse.Namespace, action: str) -> SoCo:
    try:
        return resolve_speaker(
            name=effective_speaker(args),
            ip=effective_ip(args),
            timeout=effective_timeout(args),
        )
    except Exception as exc:
        raise RuntimeError(f"Failed to {action}: {exc}") from exc


def cmd_pause(args: argparse.Namespace) -> int:
    speaker = _with_speaker(args, "pause")
    speaker.pause()
    print(f"Paused {speaker.player_name}")
    return 0


def cmd_resume(args: argparse.Namespace) -> int:
    speaker = _with_speaker(args, "resume")
    speaker.play()
    print(f"Resumed {speaker.player_name}")
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    speaker = _with_speaker(args, "skip")
    speaker.next()
    print(f"Skipped track on {speaker.player_name}")
    return 0


def cmd_prev(args: argparse.Namespace) -> int:
    speaker = _with_speaker(args, "go to previous")
    speaker.previous()
    print(f"Went to previous track on {speaker.player_name}")
    return 0


def cmd_volume(args: argparse.Namespace) -> int:
    speaker = _with_speaker(args, "set volume")
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
    speaker = _with_speaker(args, "get status")
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


def _track_artist_album(item: object) -> tuple[str, str]:
    artist = "Unknown"
    album = "Unknown"

    metadata = getattr(item, "metadata", None)
    if metadata:
        artist = _safe_getattr(metadata, "artist", artist)
        if artist == "Unknown":
            artist = _safe_getattr(metadata, "creator", artist)
        album = _safe_getattr(metadata, "album", album)

    if artist == "Unknown":
        artist = _safe_getattr(item, "creator", artist)
    if album == "Unknown":
        album = _safe_getattr(item, "album", album)
    return artist, album


def cmd_queue_list(args: argparse.Namespace) -> int:
    speaker = _with_speaker(args, "read queue")
    queue_items = speaker.get_queue(start=args.offset, max_items=args.limit)
    current_track = speaker.get_current_track_info()
    current_position = current_track.get("playlist_position")

    rows = []
    for idx, item in enumerate(queue_items, start=args.offset + 1):
        artist, album = _track_artist_album(item)
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
    speaker = _with_speaker(args, "add to queue")
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
    speaker = _with_speaker(args, "clear queue")
    speaker.clear_queue()
    print(f"Queue cleared on {speaker.player_name}")
    return 0


def _select_playlist(playlists: Sequence[PlaylistResult], selector: str) -> PlaylistResult | None:
    normalized = selector.strip().lower()
    if not normalized:
        return None

    by_id = [p for p in playlists if p.item_id.lower() == normalized]
    if len(by_id) == 1:
        return by_id[0]

    exact_title = [p for p in playlists if p.title.lower() == normalized]
    if len(exact_title) == 1:
        return exact_title[0]

    partial_title = [p for p in playlists if normalized in p.title.lower()]
    if len(partial_title) == 1:
        return partial_title[0]

    return None


def cmd_play_playlist(args: argparse.Namespace) -> int:
    speaker = _with_speaker(args, "play playlist")
    search_limit = max(1, args.limit)

    # Query first by selector; if not enough signal, expand results and resolve by id/title.
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


def cmd_group(args: argparse.Namespace) -> int:
    coordinator = resolve_speaker(
        name=args.coordinator,
        ip=None,
        timeout=effective_timeout(args),
    )
    if not args.members:
        raise RuntimeError("Pass at least one member speaker name with --members.")

    joined: list[str] = []
    for member_name in args.members:
        member = resolve_speaker(name=member_name, ip=None, timeout=effective_timeout(args))
        if member.ip_address == coordinator.ip_address:
            continue
        member.join(coordinator)
        joined.append(member.player_name or member.ip_address)

    if joined:
        print(f"Grouped with coordinator {coordinator.player_name}: {', '.join(joined)}")
    else:
        print(f"No changes. Coordinator remains {coordinator.player_name}.")
    return 0


def cmd_ungroup(args: argparse.Namespace) -> int:
    speaker = resolve_speaker(
        name=effective_speaker(args),
        ip=effective_ip(args),
        timeout=effective_timeout(args),
    )
    speaker.unjoin()
    print(f"Ungrouped {speaker.player_name}")
    return 0


def cmd_auth_spotify(args: argparse.Namespace) -> int:
    speaker = resolve_speaker(
        name=effective_speaker(args),
        ip=effective_ip(args),
        timeout=effective_timeout(args),
    )
    service = spotify_service(device=speaker)

    auth_data = service.begin_authentication()
    reg_url: str | None = None
    link_code: str | None = None

    if isinstance(auth_data, (list, tuple)):
        if len(auth_data) >= 2:
            reg_url = str(auth_data[0])
            link_code = str(auth_data[1])
    elif isinstance(auth_data, dict):
        reg_url = _opt_str(auth_data.get("regUrl")) or _opt_str(auth_data.get("reg_url"))
        link_code = _opt_str(auth_data.get("linkCode")) or _opt_str(auth_data.get("link_code"))
    elif isinstance(auth_data, str):
        reg_url = auth_data
        parsed = urlparse(auth_data)
        code_values = parse_qs(parsed.query).get("linkCode", [])
        if code_values:
            link_code = code_values[0]

    if not reg_url or not link_code:
        raise RuntimeError(f"Unexpected auth response from Sonos service: {auth_data!r}")
    print(f"Speaker: {speaker.player_name}")
    print("Complete Spotify authorization for SoCo:")
    print(f"1. Open: {reg_url}")
    print(f"2. Enter code: {link_code}")
    input("After approval is complete, press Enter to finish linking...")

    service.complete_authentication(link_code=link_code)
    print("Spotify authorization saved for this Sonos household.")
    return 0


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
    status.set_defaults(func=cmd_status)

    group = subparsers.add_parser("group", help="Group speakers under a coordinator")
    group.add_argument("--coordinator", required=True, help="Coordinator speaker name")
    group.add_argument(
        "--members",
        nargs="+",
        required=True,
        help="Speaker names to join the coordinator group",
    )
    group.add_argument("--timeout", type=int, default=None, help="Discovery timeout in seconds")
    group.set_defaults(func=cmd_group)

    ungroup = subparsers.add_parser("ungroup", help="Remove a speaker from its group")
    add_speaker_selection_args(ungroup)
    ungroup.set_defaults(func=cmd_ungroup)

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


if __name__ == "__main__":
    raise SystemExit(main())

