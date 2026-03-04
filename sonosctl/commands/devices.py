from __future__ import annotations

import argparse
import json

from sonosctl.config import effective_json_flag, effective_timeout
from sonosctl.speaker import discover_speakers, print_speakers


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
