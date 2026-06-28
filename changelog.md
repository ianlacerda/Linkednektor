# LinkedNektor — Changelog

History of implementations and iterations on the project.

## [v0.6.9] — Smart Vanity-Name Targeting, JS Click Evaluation & Polling-Based Fallbacks

### 🐛 Fixed
- **JavaScript Click Evaluation**: Replaced physical coordinate-based clicks on profile Connect buttons with programmatic JS click evaluation (`el.evaluate("el => el.click()")`) to prevent clicks from being intercepted by LinkedIn's sticky navigation bar or fixed page headers.
- **Polling Safety Loops**: Implemented a 3.0-second polling mechanism to wait for either the note text box or the Premium blocker modal to become visible after connection triggers, avoiding timing race conditions and ensuring the Premium warning popup is caught reliably.
- **Unicode Console Protection**: Reconfigured `sys.stdout` and `sys.stderr` on Windows platforms to use UTF-8 with character replacement, preventing the application from crashing with `UnicodeEncodeError` when writing emojis (like 🎯 or ❌) to non-UTF-8 terminals.
- **Vanity-Name Targeting**: Directly targets the profile owner's Connect button/link by extracting their unique vanity name from the current page URL, ensuring the bot never clicks adjacent "People also viewed" sidebar connection triggers.
- **Obfuscation-Resistant Dialog Detection**: Upgraded modal checking to dynamically scan for native HTML5 `<dialog>` elements and `[role='dialog']` elements containing premium warning terms, bypassing LinkedIn's obfuscated class names.
- **Case-Insensitive Close Buttons**: Targets the close icon/button of popups using Playwright/CSS case-insensitive flags (`button[aria-label*='Fechar' i]`, `button[aria-label*='Close' i]`), improving dismiss reliability.
- **Accurate Flow Routing**: Differentiates between connection modal and blocker overlays to accurately decide whether to stay in the current modal flow or proceed with a clean, overlay-free profile page retry.

---

## [v0.6.8] — Free Account Premium Warning Fallback

### 🐛 Fixed
- **Premium Limitation Fallback**: Resolved a bug where connection request invites failed on LinkedIn Free accounts due to monthly personalized note limits. The bot now actively detects upgrade/premium limitation modals, closes them by targeting their specific close/dismiss button selectors (or Escape as fallback), clears all modal overlays, and automatically retries the connection request without a note recursively.
- **Global Note Skipping**: Sets a session-wide flag `NOTES_BLOCKED_BY_PREMIUM` upon detection to directly skip note logic for all subsequent profiles in the run.

---

## [v0.6.7] — Database Reset & Clear History GUI Feature

### ✨ Added
- **"Clear History" GUI Button (`clear_db_button`)**:
  - Added a new button **🧹 Limpar Histórico** (or **🧹 Clear History** in English) to the Tkinter interface to reset the SQLite database.
  - Clicking the button prompts the user with a confirmation dialog. Upon validation, it calls `clear_contacted_profiles()` to delete all records from `contacted_profiles` table, enabling the bot to re-process and retry profiles from failed/interrupted runs.
  - Automatically disables the button during bot execution to prevent concurrent write/read database operations.
  - Increased GUI window height to `340x510` to accommodate the new button.

---

## [v0.6.6] — Strict Topcard Scoping & Div Listitem Isolation

### 🐛 Fixed
- **Strict Topcard Scoping**: Fixed a bug where visible Connect and "More" buttons matched elements in the Activity section (navigating to posts/publications) or sidebar because `div[role='toolbar']` matched the global nav header and `main section:first-of-type` matched the wrapper section of the entire page content. Restricted prefixes strictly to top-card boundaries (`[componentkey*='Topcard']`, `.pv-top-card`, `.pvs-profile-actions`, etc.).
- **Div-based Listitem Card Isolation**: Supported mobile layouts where cards are `div` tags with `role="listitem"` instead of `li` tags, and mutual connections are nested `li` elements. Upgraded parent traversal to filter out nested nodes of both tags, restoring exact 10-profile results search.

---

## [v0.6.5] — Strict Scoped Header Selectors & SRP Debug Utility

### ✨ Added
- **Search Results Page Debug Dump (`save_search_results_debug`)**:
  - Automatically saves the full HTML source and a PNG screenshot of the search results page to `debug_dumps/` after scrolling completes.
  - Logs a clickable `file:///` link in the terminal pointing directly to the saved HTML and image file on disk for easy click-to-open debugging.

### 🐛 Fixed
- **Strict Header Button Scoping**: Scoped visible Connect button selectors to main header wrappers (`div[role='toolbar']`, `.pvs-profile-actions`, `.pv-top-card-v2-ctas`, `.pv-top-card`, and `main section:first-of-type`) to ensure the bot only clicks the profile target's Connect button, resolving issues where uncontained generic selectors clicked "Connect" buttons for unrelated profiles in the sidebar.
- **Robust Card Isolation on SRP**: Upgraded search result card filtering to detect `li` tags and dynamically filter out any nested list items. This ensures exact name/URL mapping per search result card and avoids collecting mutual connections or fallback to `document.body` on responsive layouts.

---

## [v0.6.4] — Mobile Responsive Layout Support & Link-based Buttons

### 🐛 Fixed
- **Support for Responsive Tag-A Buttons**: Fixed a failure where the bot could not find the "Conectar" (Connect) button on profiles like Amanda Berton. Under LinkedIn's mobile responsive layout, the "Connect" action is built using an `<a>` anchor tag referencing the `/preload/custom-invite/` endpoint, rather than a standard `<button>`. Expanded selectors to support anchor-based buttons (`a[href*='custom-invite']`, `a:has-text(...)`).
- **Responsive Navigation Wait**: Adjusted SPA load protection to fall back to waiting for `a[href*='contact-info']` (Dados de contato) which is present in both desktop and mobile layouts, ensuring the profile card is fully rendered before scanning.

---

## [v0.6.3] — Mutual Connection Link Skip & Debug Dump Utility

### ✨ Added
- **HTML & Screenshot Debug Dump (`save_html_debug`)**:
  - Automatically saves the full page source HTML and a PNG screenshot to `debug_dumps/` in the project root if the bot fails to find a "Connect" button or encounters navigation/profile errors.
  - Logs a clickable `file:///` link in the terminal pointing directly to the saved HTML and image file on disk for easy click-to-open debugging.
- **Gitignore update**: Ignores `debug_dumps/` directory.

### 🐛 Fixed
- **Card-Based Profile Collection & Insights Filtering**: Rewrote the profile link extraction logic in `collect_profile_links` to loop through search result cards (`.reusable-search__result-container`) one by one, picking only the first `/in/` profile link in the card and filtering out any mutual connections or badge insights (like `.entity-result__insights` or `.entity-result__simple-insight`). This completely solves the bug where mutual connections were incorrectly visited, while preserving search targets regardless of their dynamic header tags (div or span).

---

## [v0.6.2] — SPA Load Protection & Reliable Dropdown Click

### 🐛 Fixed
- **SPA Profile Load Protection**: Added explicit wait (`page.wait_for_selector`) for `.pvs-profile-actions` or `.pv-top-card-v2-ctas` header containers before querying buttons. This solves race conditions where the SPA loads the HTML DOM structure (`domcontentloaded` triggers) but the profile action buttons have not been dynamically rendered yet.
- **Reliable Dropdown Clicks**: Prioritized direct element clicking for dropdown menus, falling back to ancestor menu-item clicks only if the direct click is blocked, guaranteeing compatibility with various dynamic link types.

---

## [v0.6.1] — Pause Responsiveness & Connection Removal Safety

### 🐛 Fixed
- **Instant Pause Action**: Refactored the delay logic (`human_delay`) to check the `pause_event` state in 0.2-second steps. The bot now pauses instantly instead of waiting for long standard delays (3-5s) to finish.
- **Connection Removal Safety**: Added check in the "More" dropdown for terms like "Remove Connection" / "Remover Conexão". If present, the bot closes the dropdown, marks the profile as `already_connected` (saving it to the SQLite DB), and skips sending a connection request to prevent accidental network removal/disconnects.
- **Scoped Dropdown Selectors**: Fixed a critical leak where the uncontained selector `span:text-is('Connect')` matched "Connect" buttons in the "People also viewed" sidebar when the profile was already connected. Dropdown selectors are now strictly scoped to `div.artdeco-dropdown__content` and use the generic `>> text=...` matching to support all HTML tags (links, buttons, divs) inside the menu.

---

## [v0.6.0] — SQLite Database & Pause/Resume Features

### ✨ Added
- **SQLite Database Integration (`src/db.py`)**:
  - Automatically initializes a local database `linkednektor.db`.
  - Stores all contacted profile URLs, names, and contact statuses (`sent` or `already_connected`).
  - Skips profile visits for contacts that have already been sent or are already in the network, saving API limits and avoiding detection.
- **Pause & Resume Controls**:
  - Thread-safe pause event (`threading.Event`) integration in bot loops.
  - Interactive **Pause/Resume** button in the Tkinter GUI to pause the bot's execution without terminating the browser session or thread.
  - Added translations for Pause and Resume buttons in Portuguese and English.

---

## [v0.5.0] — Modularization & Safety Improvements

### ✨ Added
- **Modular Project Structure**:
  - `main.py`: Entry point for the application.
  - `src/i18n.py`: Handles bilingual support and dynamic translations state.
  - `src/bot.py`: Playwright web automation tasks, human simulations, and logic.
  - `src/gui.py`: Tkinter graphical interfaces and trigger callbacks.
- **Safety Character limit verification**:
  - Warns the user on the GUI if the connection note exceeds 300 characters and automatically truncates it to prevent failure.

### 🔧 Changed
- Split the monolithic `linkednektor2_0.py` into separate components.
- Adjusted global imports so the language switcher interacts correctly with the background threading execution.

### 🐛 Fixed
- **More button Click Timeout**: Scoped the selector of the "More" button to `.pvs-profile-actions` and `.pv-top-card-v2-ctas` containers, avoiding matching hidden/covered buttons on navigation elements and preventing profile visits timeout.
- **Double Thread Execution**: Disabled the GUI "Start Search" button upon click, preventing users from spawning multiple concurrent bot threads that conflict on the same browser profile.
- **Cross-language Selector Support**: Look for both English ("More") and Portuguese ("Mais") terms regardless of active local translation to support instances where the profile UI is rendered in a different language.

---

## [v0.4.0] — Profile visits + Personalized note

### ✨ Added
- **Optional note popup** on start (`simpledialog.askstring`)
  - Appears **before** opening the browser
  - Cancel aborts execution
  - Empty = send without note
- **Function `collect_profile_links(page)`**
  - Collects all `/in/` URLs from search results
  - Deduplicates by URL
  - Extracts profile name alongside the URL
- **Function `find_connect_button_on_profile(page)`**
  - Detects **visible** "Connect" button on the profile
  - Detects "Connect" button **inside the "More" menu** (dropdown)
  - Identifies already-connected / pending profiles (returns `"already"`)
  - Returns `"found"` / `"already"` / `"not_found"`
- **Function `handle_connection_dialog(page, note_text)`**
  - If `note_text` provided → clicks "Add a note", fills `<textarea>`, clicks "Send"
  - If empty → clicks "Send without a note" directly
  - Robust handling of multiple button texts (PT/EN)
- **Function `process_page_via_profiles()`**
  - New approach: visits each profile individually
  - Replaces the old approach of clicking buttons directly on the list
  - Automatically returns to results after each profile
- **New translations** (pt/en):
  - `note_popup_title`, `note_popup_msg`
  - `visiting_profile`, `connect_visible`, `connect_in_more`
  - `adding_note`, `note_added`, `note_failed`
  - `returning_results`, `already_connected`
  - LinkedIn terms: `li_more`, `li_add_note`

### 🔧 Changed
- `run_bot()` now accepts `note_text` parameter
- `start_bot()` (GUI) opens note popup before creating the thread
- Renamed main logic from `process_page_connections` → `process_page_via_profiles`

### 📌 Motivation
The old approach clicked "Connect" buttons directly on the listing cards. Problems:
- Many profiles don't have a visible "Connect" button on the card (need to enter the profile)
- Didn't reliably allow adding a personalized note
- Hard to skip already-connected profiles

The new approach mimics human behavior: **enter profile → analyze → connect**.

---

## [v0.3.0] — Robust scroll + Container detection

### ✨ Added
- **Function `find_scroll_container(page)`** with 3 strategies:
  1. Detects `<div>` with `overflow: auto/scroll` and `scrollHeight > clientHeight`
  2. Fallback to `documentElement` / `body`
  3. Last resort: mouse wheel simulation
- **Function `scroll_page_fully()`** with adaptive logic:
  - Specific container scroll via `el.scrollTop`
  - Normal scroll via `window.scrollTo`
  - Mouse wheel via `page.mouse.wheel(0, 500)`
- Detailed logging of the scroll process (position, height, candidates)

### 🔧 Changed
- `go_to_next_page()` now scrolls to the bottom before looking for pagination
- Multiple scroll strategies to ensure results load

### 📌 Motivation
LinkedIn uses virtual scroll inside an internal container (not `window`). Previous attempts using `page.evaluate("window.scrollTo(...)")` didn't work. We needed to detect the actual scrollable container.

---

## [v0.2.0] — Advanced filters (Hiring + Location)

### ✨ Added
- **Function `apply_hiring_filter(page, title)`**
  - Opens "Hiring" dropdown
  - Types specific title OR selects "Any title"
  - Auto-selects autocomplete suggestion
- **Function `apply_location_filter(page, city)`**
  - Opens "Locations" dropdown
  - Types city and selects first suggestion
- **Function `click_show_results(page)`**
  - Clicks "Show results" to apply filters
  - Multiple fallback selectors
- "Hiring now" checkbox and "Title" field in GUI

### 🔧 Changed
- `run_bot` flow now applies filters after reaching results
- `ensure_on_results()` called between filters to ensure consistent state

---

## [v0.1.0] — Initial baseline

### ✨ Added
- **Tkinter GUI** with fields:
  - Search (required)
  - City (optional)
  - Pages (1-20)
- **Translation system** PT/EN with toggle button
- **Persistent Chromium context** (keeps login)
- **Login detection** (`is_logged_in`, `wait_for_login`)
- **Safe navigation** (`safe_goto` with retry)
- **Hardcoded limit** of 50 connections/run
- **Basic anti-detection** (`--disable-blink-features=AutomationControlled`)
- **Console output** with emojis
- **Threading** — UI doesn't freeze during execution

### 🛠️ Tech decisions
- Playwright sync API (simpler for linear script)
- Tkinter (no external dependencies)
- Single-file architecture (~1500 lines) — easier to distribute

---

## 📋 Backlog (not yet implemented)
- [ ] Dynamic note personalization (`{name}`, `{title}`)
- [ ] Exclusion list of already-contacted profiles (CSV/SQLite)
- [ ] Structured logging / CSV report
- [ ] Automatic follow-up for accepted connections
- [ ] "Weekly invitation limit" detection
- [ ] Multi-account / profile rotation
- [ ] "Scrape only" mode (without connecting)
- [ ] CRM integration (Notion / Airtable / Sheets)
- [ ] Statistics dashboard
- [ ] A/B testing of message templates
- [ ] Hashtag support in search
- [ ] Additional filters (industry, language, school)

---

## 🐛 Known Issues
- LinkedIn may change selectors at any time (selectors are inherently fragile)
- Headless mode doesn't work (LinkedIn detects it)
- New accounts have lower weekly connection limits
- Notes may be limited on free accounts (LinkedIn premium feature)
- Filters may be slow to apply on slow connections

---

## 📌 Conventions
- **Commits** (suggested): `feat:`, `fix:`, `refactor:`, `docs:`
- **Versioning**: Semantic Versioning (MAJOR.MINOR.PATCH)
- **Code style**: PEP 8, optional type hints
- **Logs**: use `t()` for all user-facing strings
