# Contributing

## Community standards

By participating, you agree to follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Setup

```bash
git clone https://github.com/andresleecom/sonosctl.git
cd sonosctl
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Testing

sonosctl requires Sonos hardware on your local network. Test manually:

```bash
sonosctl devices              # verify speaker discovery
sonosctl search "test query"  # verify Spotify search
sonosctl status               # verify playback status
```

## Pull requests

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Test with real hardware
5. Open a PR with a clear description

Keep changes focused. One feature or fix per PR.

## Reporting issues

Open an issue on [GitHub](https://github.com/andresleecom/sonosctl/issues). Include:

- sonosctl version (`pip show sonosctl`)
- Python version
- Sonos speaker model
- Error output

For security issues, see [SECURITY.md](SECURITY.md).

## Documentation expectations

If your change affects command behavior, update at least one of:

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/AI_AGENT_INTEGRATION.md` (for automation/agent behavior changes)
