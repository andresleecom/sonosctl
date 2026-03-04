from __future__ import annotations

import argparse
import os

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - python < 3.11
    import tomli as tomllib

from sonosctl.types import AppConfig, ConfigDefaults

DEFAULT_TIMEOUT = 5
DEFAULT_SEARCH_LIMIT = 5
DEFAULT_PLAY_PICK_LIMIT = 10
DEFAULT_PLAY_NON_PICK_LIMIT = 1


def default_config_path() -> str:
    return os.path.join(os.path.expanduser("~"), ".sonosctl", "config.toml")


def load_config(path: str | None) -> AppConfig:
    config_path = path or default_config_path()
    if not os.path.exists(config_path):
        return AppConfig(defaults=ConfigDefaults())

    with open(config_path, "rb") as fp:
        data = tomllib.load(fp)

    defaults = data.get("defaults", {})
    return AppConfig(
        defaults=ConfigDefaults(
            speaker=_opt_str(defaults.get("speaker")),
            ip=_opt_str(defaults.get("ip")),
            timeout=_opt_int(defaults.get("timeout")),
            search_limit=_opt_int(defaults.get("search_limit")),
            json_output=_opt_bool(defaults.get("json")),
            replace_queue=_opt_bool(defaults.get("replace_queue")),
        )
    )


def _opt_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def _opt_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _opt_bool(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
    return None


def effective_timeout(args: argparse.Namespace) -> int:
    value = args.timeout if args.timeout is not None else args.config_defaults.timeout
    return value if value is not None else DEFAULT_TIMEOUT


def effective_speaker(args: argparse.Namespace) -> str | None:
    return args.speaker if args.speaker is not None else args.config_defaults.speaker


def effective_ip(args: argparse.Namespace) -> str | None:
    return args.ip if args.ip is not None else args.config_defaults.ip


def effective_search_limit(args: argparse.Namespace, fallback: int) -> int:
    value = args.limit if args.limit is not None else args.config_defaults.search_limit
    if value is None:
        return fallback
    return max(1, value)


def effective_json_flag(args: argparse.Namespace) -> bool:
    if args.json is not None:
        return args.json
    if args.config_defaults.json_output is not None:
        return args.config_defaults.json_output
    return False


def effective_replace_queue(args: argparse.Namespace) -> bool:
    if args.replace_queue is not None:
        return args.replace_queue
    if args.config_defaults.replace_queue is not None:
        return args.config_defaults.replace_queue
    return False
