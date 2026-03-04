from __future__ import annotations

from dataclasses import dataclass


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
class FavoriteResult:
    title: str
    kind: str
    item_id: str
    uri: str
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
