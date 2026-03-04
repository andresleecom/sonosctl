from __future__ import annotations

import argparse
from urllib.parse import parse_qs, urlparse

from sonosctl.config import effective_ip, effective_speaker, effective_timeout, _opt_str
from sonosctl.speaker import resolve_speaker
from sonosctl.spotify import spotify_service


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
