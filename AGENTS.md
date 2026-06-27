# AGENTS.md — LinkedNektor

> Standing instructions for all agents working on this project.
> Read `SKILLS.md` for full project context and `CHANGELOG.md` for history before making changes.

---

## 🎯 Project Snapshot

**LinkedNektor** is a Python + Playwright LinkedIn automation bot with a Tkinter GUI.
It sends personalized connection requests at scale for client prospecting.

- **Entry point:** `main.py`
- **Architecture:** Modular structure (GUI, Bot automation, SQLite database, and i18n translations separated inside `src/` folder)
- **Stack:** Python 3.x, Playwright (sync), Tkinter, SQLite 3, Chromium persistent context
- **Languages:** UI/console bilingual (PT-BR / EN) via `t()` helper inside `src/i18n.py`

---

## 📚 Required Reading

Before any task, read in this order:

1. `SKILLS.md` — full project context, LinkedIn quirks, anti-detection strategies
2. `CHANGELOG.md` — version history and motivations behind each change
3. `src/bot.py`, `src/gui.py`, `src/db.py`, `src/i18n.py` — current code modular files

If any of these files conflict with a user request, ask for clarification before proceeding.

---

## 🧭 Core Conventions

### Code style

- **PEP 8** strict
- **Modular architecture** — keep GUI, Bot and Translation separate. Do not write everything into a single file unless explicitly requested.
- **No new external dependencies** without asking — current deps are stdlib + `playwright` only
- **Type hints optional**, but encouraged on new public functions
- **Docstrings** required on new functions (1-line minimum)

### Bilingual system (i18n) — STRICT

- **Never hardcode user-facing strings.** Always use `t("key")` from `src.i18n`
- **Every new string requires BOTH `pt` and `en` entries** in `TRANSLATIONS` inside `src/i18n.py`
- LinkedIn UI terms use the `li_*` key prefix (e.g., `li_connect`, `li_more`)
- When adding selectors that depend on visible text, try BOTH language variants

### Anti-detection (CRITICAL)

- **Always add `human_delay(min, max)` between LinkedIn actions** (2-5s typical)
- **Type characters one-by-one** with `delay=random.randint(50, 150)` for inputs (or `30, 80` in dialog custom message inputs)
- **Never enable headless mode** — LinkedIn detects it
- **Never increase `max_per_run = 50`** without explicit user approval
- Preserve `--disable-blink-features=AutomationControlled` in launch args

### Playwright patterns

- **Always provide multiple fallback selectors** — LinkedIn DOM changes frequently
- **Wrap risky operations in try/except** with logging via `t("error", msg=...)`
- **Call `ensure_on_results(page, search_url)`** before assuming page state
- **Use `safe_goto()`** instead of `page.goto()` for navigation
- **Prefer `:has-text()` and `:text-is()`** selectors over fragile class names

### GUI / Threading

- **Never touch Tkinter widgets from the bot thread** — only from the main thread
- Bot must run in a `daemon=True` thread
- GUI strings must use `t()` and be updated by `update_gui_language()`

---

## 🚫 Hard Rules — Do NOT

- ❌ Don't run the bot headless
- ❌ Don't hardcode user-facing strings (use `t()`)
- ❌ Don't add new external dependencies without asking
- ❌ Don't remove anti-detection features (delays, persistent context, etc.)
- ❌ Don't exceed `max_per_run = 50` without explicit user approval
- ❌ Don't break the bilingual structure (PT must mirror EN and vice versa)
- ❌ Don't commit Chrome profile data (`~/linkednektor_profile`)

---

## ✅ Soft Rules — Prefer to

- ✅ Add console logs via `print(f"  {t('your_key', ...)}")` for visibility
- ✅ Use emoji prefixes in logs for scanability (🔍 ✅ ❌ ⚠️ 📄 👤)
- ✅ Preserve the existing function naming conventions
- ✅ When fixing a selector, ADD a new fallback rather than REPLACE the old one
- ✅ Update `CHANGELOG.md` with any non-trivial change
- ✅ Use Plan mode for changes touching multiple functions

---

## 🧪 Verification Workflow

When implementing a feature:

1. **Plan first** — outline the change in the task list before editing
2. **Identify affected modules** (e.g., `src/bot.py`, `src/gui.py`, `src/i18n.py`)
3. **Add translation keys first** if the feature has user-facing text
4. **Implement** with multiple fallback selectors where applicable
5. **Update `CHANGELOG.md`** with a new entry describing what & why
6. **Do NOT auto-run the bot** — LinkedIn automation can rate-limit. Ask the user to test manually.

If you use the browser subagent to verify changes, **DO NOT log into LinkedIn with the user's account** — only test on the static/login-free portions.

---

## 🔮 Common Tasks Reference

### Add a new LinkedIn selector

- Add fallback selectors (don't replace)
- Test BOTH `li_*` PT-BR and EN variants
- Wrap in try/except returning gracefully

### Add a new filter

- Follow the pattern of `apply_hiring_filter()` / `apply_location_filter()`
- Always call `click_show_results()` at the end
- Always call `ensure_on_results()` after the filter

### Add a new GUI field

- Add label + widget in the GUI section
- Add translation keys (`label_*`, `placeholder_*`)
- Update `update_gui_language()` to refresh on language toggle
- Pass the value through `start_bot_thread()` → `run_bot()`

### Modify the message/note flow

- Note has a **300-character limit** on LinkedIn (validate!)
- Free accounts have **weekly note limits** — handle gracefully
- Always test both "Send" and "Send without a note" paths

---

## 📦 Backlog Awareness

When proposing changes, check `CHANGELOG.md`'s backlog section. If your task matches a backlog item, mention it and align with the original intent.

---

## 🆘 When in Doubt

- **Ask the user** before making architectural changes
- **Prefer additive changes** over destructive ones
- **Preserve backwards compatibility** of the GUI/CLI surface
- **Log uncertainty** to console rather than silently continuing
