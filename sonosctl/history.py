from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from sonosctl.config import config_dir


@dataclass
class PlaybackHistoryEntry:
    observed_at: str
    speaker: str
    track: str
    artist: str
    album: str
    source: str
    state: str
    duration: str
    position: str
    group_coordinator: str | None = None


def history_path() -> Path:
    return Path(config_dir()) / "history.jsonl"


def _normalize(value: str) -> str:
    return value.strip().lower()


def _identity(entry: PlaybackHistoryEntry) -> tuple[str, str, str, str, str]:
    return (
        _normalize(entry.speaker),
        _normalize(entry.track),
        _normalize(entry.artist),
        _normalize(entry.album),
        _normalize(entry.source),
    )


def _ensure_parent_dir(path: Path) -> None:
    os.makedirs(path.parent, exist_ok=True)


def _load_last_entry(path: Path) -> PlaybackHistoryEntry | None:
    if not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8") as fp:
            lines = fp.readlines()
    except OSError:
        return None

    for line in reversed(lines):
        raw = line.strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            try:
                return PlaybackHistoryEntry(**data)
            except TypeError:
                continue
    return None


def append_playback_history(
    *,
    speaker: str,
    track: str,
    artist: str,
    album: str,
    source: str,
    state: str,
    duration: str,
    position: str,
    group_coordinator: str | None = None,
) -> PlaybackHistoryEntry | None:
    if state != "PLAYING":
        return None
    if track == "Unknown" and artist == "Unknown":
        return None

    path = history_path()
    _ensure_parent_dir(path)

    entry = PlaybackHistoryEntry(
        observed_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        speaker=speaker,
        track=track,
        artist=artist,
        album=album,
        source=source,
        state=state,
        duration=duration,
        position=position,
        group_coordinator=group_coordinator,
    )

    last_entry = _load_last_entry(path)
    if last_entry and _identity(last_entry) == _identity(entry):
        return None

    with path.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(asdict(entry), ensure_ascii=True) + "\n")
    return entry


def read_playback_history(limit: int = 20, speaker: str | None = None) -> list[PlaybackHistoryEntry]:
    path = history_path()
    if not path.exists():
        return []

    entries: list[PlaybackHistoryEntry] = []
    try:
        with path.open("r", encoding="utf-8") as fp:
            for line in fp:
                raw = line.strip()
                if not raw:
                    continue
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if not isinstance(data, dict):
                    continue
                try:
                    entry = PlaybackHistoryEntry(**data)
                except TypeError:
                    continue
                if speaker and _normalize(entry.speaker) != _normalize(speaker):
                    continue
                entries.append(entry)
    except OSError:
        return []

    if limit <= 0:
        return entries
    return entries[-limit:]
