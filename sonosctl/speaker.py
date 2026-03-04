from __future__ import annotations

import argparse
from typing import Sequence

import soco
from soco import SoCo

from sonosctl.config import DEFAULT_TIMEOUT, effective_ip, effective_speaker, effective_timeout


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


def with_speaker(args: argparse.Namespace, action: str) -> SoCo:
    try:
        return resolve_speaker(
            name=effective_speaker(args),
            ip=effective_ip(args),
            timeout=effective_timeout(args),
        )
    except Exception as exc:
        raise RuntimeError(f"Failed to {action}: {exc}") from exc
