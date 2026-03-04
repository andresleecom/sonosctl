from __future__ import annotations

import argparse
import json

from sonosctl.config import effective_json_flag
from sonosctl.speaker import with_speaker


def _repeat_mode_label(value: object) -> str:
    if value == "ONE":
        return "one"
    if value is True:
        return "all"
    return "off"


def cmd_shuffle(args: argparse.Namespace) -> int:
    speaker = with_speaker(args, "set shuffle")
    if args.mode is None:
        current = bool(speaker.shuffle)
        if effective_json_flag(args):
            print(
                json.dumps(
                    {
                        "speaker": speaker.player_name or speaker.ip_address,
                        "shuffle": current,
                    },
                    indent=2,
                )
            )
            return 0
        print(f'{speaker.player_name} shuffle: {"on" if current else "off"}')
        return 0

    desired = args.mode == "on"
    speaker.shuffle = desired
    print(f'{speaker.player_name} shuffle set to {"on" if desired else "off"}')
    return 0


def cmd_repeat(args: argparse.Namespace) -> int:
    speaker = with_speaker(args, "set repeat")
    if args.mode is None:
        current = _repeat_mode_label(speaker.repeat)
        if effective_json_flag(args):
            print(
                json.dumps(
                    {
                        "speaker": speaker.player_name or speaker.ip_address,
                        "repeat": current,
                    },
                    indent=2,
                )
            )
            return 0
        print(f"{speaker.player_name} repeat: {current}")
        return 0

    mapping = {"off": False, "all": True, "one": "ONE"}
    desired = mapping[args.mode]
    speaker.repeat = desired
    print(f"{speaker.player_name} repeat set to {args.mode}")
    return 0


def cmd_crossfade(args: argparse.Namespace) -> int:
    speaker = with_speaker(args, "set crossfade")
    if args.mode is None:
        current = bool(speaker.cross_fade)
        if effective_json_flag(args):
            print(
                json.dumps(
                    {
                        "speaker": speaker.player_name or speaker.ip_address,
                        "crossfade": current,
                    },
                    indent=2,
                )
            )
            return 0
        print(f'{speaker.player_name} crossfade: {"on" if current else "off"}')
        return 0

    desired = args.mode == "on"
    speaker.cross_fade = desired
    print(f'{speaker.player_name} crossfade set to {"on" if desired else "off"}')
    return 0
