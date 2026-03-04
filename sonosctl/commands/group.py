from __future__ import annotations

import argparse

from sonosctl.config import effective_ip, effective_speaker, effective_timeout
from sonosctl.speaker import resolve_speaker


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
