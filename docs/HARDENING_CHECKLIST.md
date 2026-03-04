# Hardening Checklist

Use this checklist before publishing and operating `sonosctl` in shared environments.

## Code and Repo Hygiene

- [ ] No secrets in source code or documentation
- [ ] `.gitignore` excludes virtualenvs, caches, build artifacts, local config files
- [ ] `LICENSE` and `SECURITY.md` present
- [ ] `README.md` installation and incident procedures validated

## Dependency Security

- [ ] Pin/monitor dependencies (`soco`, transitive deps)
- [ ] Enable Dependabot and GitHub security alerts
- [ ] Run `pip-audit` before each release

Example:

```bash
python -m pip install pip-audit
pip-audit
```

## Runtime Safety

- [ ] Run CLI from trusted control host on same LAN as Sonos
- [ ] Keep local VPN disabled during operation
- [ ] Restrict who can run auth and group commands
- [ ] Use explicit `--speaker` in shared terminals

## Credential and Token Handling

- [ ] Never commit `~/.sonosctl/config.toml`
- [ ] Re-auth with `auth-spotify` when token errors occur
- [ ] Do not share terminal history containing auth links/codes

## Release Process

- [ ] Tag releases (`vX.Y.Z`)
- [ ] Build artifacts with `python -m build`
- [ ] Publish via trusted maintainer account only
- [ ] Add release notes including security-impacting changes

## Incident Response

- [ ] Keep operator runbook available (`docs/OPERATOR_GUIDE.md`)
- [ ] Capture command output and environment details for escalation
- [ ] Rotate/re-auth credentials if compromise is suspected
