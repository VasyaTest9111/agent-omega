# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
make setup      # install python-dotenv, python-telegram-bot, google-generativeai, requests
make init       # regenerate SYSTEM_CONFIG.py (gitignored, not committed — see Architecture)
make bot        # run the live Telegram bot (telegram_bot.py)
make engine     # run uos_engine.py standalone (init dependency runs first)
make bot-test   # run bot_manager.py standalone (init dependency runs first)
make run        # run task_orchestrator.py (init dependency runs first)
make lint       # pylint if available, else flake8
make clean      # remove __pycache__, *.pyc/*.pyo, .pytest_cache, and SYSTEM_CONFIG.py
```

No test suite exists yet (`make test` no-ops if no `test_*.py`/`tests/` files are present).

Syntax/lint/security checks run in CI (`.github/workflows/ci.yml`) via `py_compile`, `flake8`, and `bandit` on every push to `main`/`develop`/`master`/`claude/**`/`vibe/**` and on PRs. The CI integration-test job requires `GH_TOKEN` and `OWNER_M` secrets to import `github_client` successfully.

## Architecture

This repo contains two unrelated things layered on top of each other:

1. **A live Telegram bot** (`telegram_bot.py`, `github_client.py`, `gemini_client.py`) — the part that actually runs in production, deployed on Railway (`Procfile`, `railway.json`). It answers Telegram commands (`/repos`, `/branches`, `/commits`, `/prs`, `/issues`, `/summary`) by calling the GitHub REST API directly via `requests`, and free-text messages via Gemini (`gemini-2.0-flash`), injecting GitHub repo context into the prompt when the message contains GitHub-related keywords.

2. **The "UOS-Core" / "Agent OMEGA" system** (`uos_engine.py`, `task_orchestrator.py`, `bot_manager.py`, `initialize_project.py`) — an older, largely aspirational multi-node orchestration layer that predates and does not integrate with the Telegram bot above. Its `main()` entry points log elaborate "system status" banners but the actual message routing (`BotManager.process_telegram_message` / `process_gemini_request`) is unused mock plumbing — nothing in `telegram_bot.py` calls into it. Treat these files as a separate legacy subsystem, not the runtime path for the bot.

**Environment variable naming is non-standard and split across two conventions** — check both before assuming a var is missing:
- Bot runtime (`github_client.py`, `telegram_bot.py`): `GH_TOKEN`, `OWNER_M`, `GEMINI_API_KEY`, `TELEGRAM_TOKEN_1`
- Legacy multi-node system (`bot_manager.py`): `TELEGRAM_TOKEN_1` through `TELEGRAM_TOKEN_6`, `GEMINI_API_KEY`

**`SYSTEM_CONFIG.py` is a generated, gitignored file**, not source. `initialize_project.py` writes it on demand (`class SystemState` with `state`/`registry`/`operational_mode`). `uos_engine.py` and `task_orchestrator.py` both try to import `SystemState` from it and fall back to an identical inline `SystemState` stub if the file doesn't exist — so the legacy system runs fine without ever calling `make init`.

**Circular import avoidance**: `bot_manager.py` imports `uos_engine.UOSEngine` lazily (inside `_route_to_uos_engine`, not at module top) specifically to break a circular dependency, since `uos_engine.py` also imports `BotManager` at module scope. Keep that import lazy if touching either file.

**Docs are split EN/UA** (`README.md` / `README_UA.md`) and describe the legacy UOS-Core/Agent OMEGA philosophy (`AGENT_OMEGA_v1.0.md`, `VASYA_CORE_v4.0.md`, `SEMANTIC_CORE_v5.0.md`, `docs/PHILOSOPHY.md`, `docs/LUN_EFFECT.md`) — a cognitive-framework prompt-engineering methodology unrelated to the bot's runtime behavior. Don't conflate the two when making changes: code changes to the bot belong in `telegram_bot.py`/`github_client.py`/`gemini_client.py`; the `*_CORE_*.md` files are prompt/methodology documents, not architecture docs for the running system.
