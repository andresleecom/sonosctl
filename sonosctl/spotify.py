from __future__ import annotations

from soco import SoCo
from soco.music_services import MusicService

from sonosctl.config import DEFAULT_SEARCH_LIMIT
from sonosctl.types import FavoriteResult, PlaylistResult, TrackResult


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


def _favorite_kind(item: object) -> str:
    item_class = _safe_getattr(item, "item_class", "").lower()
    ref = getattr(item, "reference", None)
    ref_class = _safe_getattr(ref, "item_class", "").lower() if ref else ""
    candidate = f"{item_class} {ref_class}"

    if "playlist" in candidate:
        return "playlist"
    if "musictrack" in candidate or "track" in candidate:
        return "track"
    if "radio" in candidate or "audiobroadcast" in candidate:
        return "radio"
    if "album" in candidate:
        return "album"
    return "other"


def list_favorites(
    speaker: SoCo,
    limit: int = 50,
    offset: int = 0,
    kind_filter: str = "all",
    query: str = "",
) -> list[FavoriteResult]:
    result = speaker.music_library.get_sonos_favorites(start=offset, max_items=limit)
    favorites: list[FavoriteResult] = []

    for item in result:
        kind = _favorite_kind(item)
        title = _safe_getattr(item, "title", "Unknown")
        item_id = _safe_getattr(item, "item_id", "")
        uri = _safe_getattr(item, "uri", "")
        if not uri:
            uri = _safe_getattr(getattr(item, "reference", None), "uri", "")

        favorites.append(
            FavoriteResult(
                title=title,
                kind=kind,
                item_id=item_id,
                uri=uri,
                item=item,
            )
        )

    if kind_filter != "all":
        target = "playlist" if kind_filter == "playlists" else "track"
        favorites = [x for x in favorites if x.kind == target]

    if query:
        q = query.lower().strip()
        favorites = [x for x in favorites if q in x.title.lower() or q in x.uri.lower()]

    return favorites
