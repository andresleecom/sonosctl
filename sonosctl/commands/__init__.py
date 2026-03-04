from sonosctl.commands.auth import cmd_auth_spotify
from sonosctl.commands.devices import cmd_devices
from sonosctl.commands.group import cmd_group, cmd_ungroup
from sonosctl.commands.modes import cmd_crossfade, cmd_repeat, cmd_shuffle
from sonosctl.commands.playback import cmd_next, cmd_pause, cmd_play, cmd_prev, cmd_resume, cmd_status, cmd_volume
from sonosctl.commands.playlist import cmd_play_playlist
from sonosctl.commands.queue import cmd_queue_add, cmd_queue_clear, cmd_queue_list
from sonosctl.commands.search import cmd_playlists, cmd_search

__all__ = [
    "cmd_auth_spotify",
    "cmd_crossfade",
    "cmd_devices",
    "cmd_group",
    "cmd_next",
    "cmd_pause",
    "cmd_play",
    "cmd_play_playlist",
    "cmd_playlists",
    "cmd_prev",
    "cmd_queue_add",
    "cmd_queue_clear",
    "cmd_queue_list",
    "cmd_repeat",
    "cmd_resume",
    "cmd_search",
    "cmd_shuffle",
    "cmd_status",
    "cmd_ungroup",
    "cmd_volume",
]
