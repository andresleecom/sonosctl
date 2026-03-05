from __future__ import annotations

import argparse
import json
import time

from sonosctl.config import effective_ip, effective_json_flag, effective_speaker, effective_timeout
from sonosctl.speaker import discover_speakers, resolve_speaker


def _speaker_name(device: object) -> str:
    name = getattr(device, "player_name", None)
    return str(name) if name else "Unknown"


def _is_joined_to(member: object, coordinator: object) -> bool:
    group = getattr(member, "group", None)
    coord = getattr(group, "coordinator", None) if group else None
    return bool(coord and getattr(coord, "ip_address", None) == getattr(coordinator, "ip_address", None))


def cmd_group(args: argparse.Namespace) -> int:
    coordinator = resolve_speaker(
        name=args.coordinator,
        ip=None,
        timeout=effective_timeout(args),
    )
    if not args.members:
        raise RuntimeError("Pass at least one member speaker name with --members.")

    wait_seconds = max(0.0, float(args.wait))
    joined: list[str] = []
    pending: list[tuple[object, str]] = []
    for member_name in args.members:
        member = resolve_speaker(name=member_name, ip=None, timeout=effective_timeout(args))
        if member.ip_address == coordinator.ip_address:
            continue
        member.join(coordinator)
        pending.append((member, member.player_name or member.ip_address))

    if wait_seconds > 0 and pending:
        deadline = time.time() + wait_seconds
        while time.time() < deadline and pending:
            still_pending: list[tuple[object, str]] = []
            for member, name in pending:
                if _is_joined_to(member, coordinator):
                    joined.append(name)
                else:
                    still_pending.append((member, name))
            pending = still_pending
            if pending:
                time.sleep(0.25)
    else:
        joined = [name for _, name in pending]

    failed = [name for _, name in pending]

    if joined:
        print(f"Grouped with coordinator {coordinator.player_name}: {', '.join(joined)}")
    if failed:
        print(f"Pending (not confirmed yet): {', '.join(failed)}")
    else:
        if not joined:
            print(f"No changes. Coordinator remains {coordinator.player_name}.")
    return 0


def cmd_ungroup(args: argparse.Namespace) -> int:
    speaker = resolve_speaker(
        name=effective_speaker(args),
        ip=effective_ip(args),
        timeout=effective_timeout(args),
    )
    wait_seconds = max(0.0, float(args.wait))
    speaker.unjoin()
    if wait_seconds > 0:
        deadline = time.time() + wait_seconds
        confirmed = False
        while time.time() < deadline:
            group = getattr(speaker, "group", None)
            members = list(getattr(group, "members", [])) if group else []
            if len(members) <= 1:
                confirmed = True
                break
            time.sleep(0.25)
        if confirmed:
            print(f"Ungrouped {speaker.player_name}")
        else:
            print(f"Ungroup requested for {speaker.player_name} (not yet confirmed)")
        return 0

    print(f"Ungrouped {speaker.player_name}")
    return 0


def cmd_groups(args: argparse.Namespace) -> int:
    devices = discover_speakers(timeout=effective_timeout(args))
    if not devices:
        print("No Sonos speakers found on your network.")
        return 0

    groups = list(devices[0].all_groups)
    payload_groups = []
    for group in groups:
        coordinator = getattr(group, "coordinator", None)
        members = list(getattr(group, "members", []))
        payload_groups.append(
            {
                "coordinator": _speaker_name(coordinator),
                "members": [_speaker_name(m) for m in members],
            }
        )

    payload_groups.sort(key=lambda g: g["coordinator"].lower())

    if effective_json_flag(args):
        print(json.dumps({"groups": payload_groups}, indent=2))
        return 0

    print("Current Sonos groups:")
    for idx, group in enumerate(payload_groups, start=1):
        print(f'{idx}. {group["coordinator"]} <- {", ".join(group["members"])}')
    return 0
