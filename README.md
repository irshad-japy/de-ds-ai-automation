# de_ds_ai_automation

Repo layout:
- modules/: each PoC is a self-contained module with a standardized entrypoint and tests
- modules/common/: shared utilities
- archive/: retired PoCs

Quick start:
1. Inspect modules/ and choose a PoC folder.
2. Run a PoC (example): `python -m modules.poc_name.main`
3. Run tests: `pytest modules/<poc>/tests`

Refactor workflow:
1. Inventory PoCs and dependencies.
2. Move shared code to modules/common.
3. Make each PoC import common utilities instead of copying code.
4. Add tests and CI gradually.

