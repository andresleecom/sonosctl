from __future__ import annotations

from soco import SoCo
from soco.music_services import MusicService

from sonosctl.config import DEFAULT_SEARCH_LIMIT
from sonosctl.types import PlaylistResult, TrackResult


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


def track_artist_album(item: object) -> tuple[str, str]:
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
