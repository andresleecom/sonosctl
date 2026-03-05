# Open Source Release Checklist

Use this checklist before publishing a new `sonosctl` release.

## Product and Docs

- [ ] `README.md` command list is current
- [ ] New flags/subcommands documented
- [ ] `CHANGELOG.md` updated
- [ ] `docs/ARCHITECTURE.md` updated for structural changes
- [ ] `docs/AI_AGENT_INTEGRATION.md` updated for automation-impacting changes

## Security and Legal

- [ ] `LICENSE` present and correct
- [ ] `SECURITY.md` contact and policy still valid
- [ ] Independence notice still present in `README.md`
- [ ] No secrets in code/docs/examples

## Quality Gates

- [ ] `python -m sonosctl --help` passes
- [ ] `python -m compileall sonosctl` passes
- [ ] Hardware smoke test on at least one Sonos speaker:
  - [ ] `devices`
  - [ ] `status --json`
  - [ ] `play` / `play-playlist`
  - [ ] `group`/`ungroup`/`groups`

## Packaging and Release

- [ ] Version bumped in `pyproject.toml`
- [ ] `python -m build` passes
- [ ] Git tag created (`vX.Y.Z`)
- [ ] GitHub release notes published
- [ ] PyPI publish completed (if applicable)

## Post-release

- [ ] Verify install from PyPI in a clean environment
- [ ] Verify issue templates and PR template are active
- [ ] Announce release and link changelog
