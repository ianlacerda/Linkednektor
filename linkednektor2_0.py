import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from playwright.sync_api import sync_playwright
import time
import random
import urllib.parse
import threading
import os


# ===== LANGUAGE SYSTEM =====
TRANSLATIONS = {
    "pt": {
        # GUI
        "window_title": "LinkedNektor",
        "label_search": "Pesquisa (ex: Tech Recruiter):",
        "label_city": "Cidade (opcional):",
        "label_title": "Cargo 'Contratando já' (opcional):",
        "label_pages": "Páginas (1-20):",
        "checkbox_hiring": "Contratando já",
        "btn_start": "🚀 Iniciar Buscas",
        "btn_language": "🌐 English",
        "warning_title": "Aviso",
        "warning_fill": "Preencha o campo 'Pesquisa'",
        "note_popup_title": "Nota de Conexão",
        "note_popup_msg": "Digite uma nota para enviar com a solicitação\n(deixe vazio para enviar sem nota):",
        "note_set": "📝 Nota definida: '{note}'",
        "note_empty": "📝 Sem nota (enviar direto)",

        # Console
        "starting": "--- Iniciando LinkedNektor ---",
        "search_label": "Pesquisa",
        "city_label": "Cidade",
        "title_label": "Cargo (Contratando já)",
        "hiring_label": "Contratando já",
        "pages_label": "Páginas",
        "note_label": "Nota",
        "none": "(nenhum)",
        "any": "(qualquer)",
        "yes": "Sim",
        "no": "Não",
        "opening_browser": "Abrindo o navegador...",
        "accessing_linkedin": "Acessando o LinkedIn...",
        "not_logged_in": (
            "\n⚠️ NÃO ESTÁ LOGADO!"
            "\n   Faça login no navegador que abriu."
            "\n   O bot aguardará automaticamente..."
        ),
        "waiting_login": "⏳ Aguardando login... ({seconds}s)",
        "login_detected": "✅ Login detectado! Continuando...",
        "login_timeout": "❌ Timeout de login ({seconds}s). Abortando.",
        "searching_for": "🔍 Buscando por:",
        "waiting_load": "Aguardando carregamento...",
        "hiring_not_selected": "🏢 'Contratando já' não selecionado.",
        "no_city": "📍 Sem cidade.",
        "final_url": "📍 URL final:",
        "page_of": "📄 PÁGINA {current} de {total}",
        "scrolling": "Rolando página...",
        "scroll_container": "  📦 Container: {selector} (altura: {height}px, visível: {visible}px)",
        "scroll_progress": "  ↓ Scroll {current}/{total} (posição: {pos}px)",
        "scroll_complete": "  ✅ Scroll completo. Altura rolada: {height}px",
        "scroll_no_container": "  ⚠️ Nenhum container com scroll encontrado. Tentando fallback...",
        "searching_connect": "🔍 Buscando 'Conectar'...",
        "found_buttons": "Encontrados: {count}",
        "clicking_connect": "[{num}] Clicando 'Conectar'...",
        "connection_sent": "✅ Conexão {count} enviada!",
        "sent_direct": "ℹ️ Enviado direto",
        "no_buttons_left": "ℹ️ Nenhum botão 'Conectar' restante.",
        "all_tried": "ℹ️ Todos os botões visíveis já foram tentados.",
        "max_failures": "⚠️ {count} falhas consecutivas. Parando nesta página.",
        "page_stats": "📊 Página {page}: {sent} | Total: {total}",
        "limit_reached": "⚠️ Limite de {max} atingido!",
        "next_page": "📄 Indo para a próxima página...",
        "next_page_ok": "✅ Próxima página!",
        "no_more_pages": "❌ Não há mais páginas.",
        "finished": "🎉 LinkedNektor FINALIZADO!",
        "finished_pages": "Páginas: {pages}",
        "finished_connections": "Conexões: {connections}",
        "error": "❌ Erro: {msg}",
        "left_results": "⚠️ Saiu da página de resultados! URL: {url}",
        "going_back": "Voltando para os resultados...",
        "cant_go_back": "❌ Não conseguiu voltar. Abortando esta página.",
        "navigated_profile": "⚠️ Navegou para perfil! Voltando...",
        "unexpected_state": "⚠️ Estado inesperado. Tentando Escape...",
        "force_click": "Tentando clique forçado...",
        "failed_skip": "❌ Falhou. Marcando e pulando...",
        "btn_error": "❌ Erro no botão idx={idx}: {msg}",
        "not_on_results": "⚠️ Não estamos nos resultados. Voltando...",
        "navigating_feed": "Navegando para o feed...",
        "nav_error_retrying": "⚠️ Navegação interrompida. Tentando novamente ({attempt}/{max})...",
        "waiting_page_stable": "Aguardando página estabilizar...",
        "ensuring_results": "🔍 Verificando se estamos nos resultados...",
        "back_to_results": "✅ De volta aos resultados.",
        "recovering_url": "🔄 Recuperando URL de resultados...",

        # Profile visit
        "collecting_profiles": "🔍 Coletando links de perfis na página...",
        "found_profiles": "👤 Encontrados {count} perfis",
        "visiting_profile": "👤 [{num}/{total}] Visitando perfil: {name}",
        "connect_visible": "✅ Botão 'Conectar' visível no perfil",
        "connect_in_more": "🔽 'Conectar' encontrado no menu 'Mais'",
        "connect_not_found": "❌ Botão 'Conectar' não encontrado neste perfil",
        "already_connected": "ℹ️ Já conectado ou pendente",
        "adding_note": "📝 Adicionando nota...",
        "note_added": "✅ Nota adicionada",
        "note_failed": "⚠️ Falha ao adicionar nota, enviando sem nota",
        "returning_results": "↩️ Voltando para resultados...",
        "profile_error": "❌ Erro ao visitar perfil: {msg}",
        "skipping_profile": "⏭️ Pulando perfil (sem URL válida)",

        # Filtros
        "applying_hiring": "🏢 Aplicando filtro 'Contratando já'...",
        "found_selector": "✅ Encontrado: {sel}",
        "dropdown_open": "✅ Dropdown aberto",
        "typing_title": "Digitando cargo: '{title}'...",
        "input_found": "✅ Input encontrado: {sel}",
        "typed": "✅ '{text}' digitado",
        "suggestion_selected": "✅ Sugestão: '{text}'",
        "any_title_selected": "✅ 'Qualquer cargo' selecionado",
        "hiring_not_found": "❌ 'Contratando já' não encontrado.",
        "input_not_found": "❌ Input não encontrado.",
        "applying_location": "📍 Aplicando filtro de localidade: {city}",
        "location_not_found": "❌ 'Localidades' não encontrado.",
        "selected_location": "✅ Selecionado: '{text}'",
        "looking_show_results": "Procurando 'Exibir resultados'...",
        "show_results_clicked": "✅ 'Exibir resultados' clicado!",
        "show_results_not_found": "⚠️ Botão 'Exibir resultados' não encontrado.",

        # LinkedIn elements (PT-BR)
        "li_connect": "Conectar",
        "li_connect_alt": "Connect",
        "li_send_no_note": "Enviar sem nota",
        "li_send_now": "Enviar agora",
        "li_send": "Enviar",
        "li_hiring": "Contratando já",
        "li_any_title": "Qualquer cargo",
        "li_locations": "Localidades",
        "li_show_results": "Exibir resultados",
        "li_show_results_alt": "Mostrar resultados",
        "li_next": "Próxima",
        "li_hiring_input": "Contratando para cargo",
        "li_add_location": "Adicionar localidade",
        "li_more": "Mais",
        "li_add_note": "Adicionar nota",
    },
    "en": {
        # GUI
        "window_title": "LinkedNektor",
        "label_search": "Search (e.g.: Tech Recruiter):",
        "label_city": "City (optional):",
        "label_title": "Title for 'Hiring' filter (optional):",
        "label_pages": "Pages (1-20):",
        "checkbox_hiring": "Hiring now",
        "btn_start": "🚀 Start Search",
        "btn_language": "🌐 Português",
        "warning_title": "Warning",
        "warning_fill": "Please fill the 'Search' field",
        "note_popup_title": "Connection Note",
        "note_popup_msg": "Type a note to send with the request\n(leave empty to send without note):",
        "note_set": "📝 Note set: '{note}'",
        "note_empty": "📝 No note (send directly)",

        # Console
        "starting": "--- Starting LinkedNektor ---",
        "search_label": "Search",
        "city_label": "City",
        "title_label": "Title (Hiring)",
        "hiring_label": "Hiring now",
        "pages_label": "Pages",
        "note_label": "Note",
        "none": "(none)",
        "any": "(any)",
        "yes": "Yes",
        "no": "No",
        "opening_browser": "Opening browser...",
        "accessing_linkedin": "Accessing LinkedIn...",
        "not_logged_in": (
            "\n⚠️ NOT LOGGED IN!"
            "\n   Please log in to the browser that opened."
            "\n   The bot will wait automatically..."
        ),
        "waiting_login": "⏳ Waiting for login... ({seconds}s)",
        "login_detected": "✅ Login detected! Continuing...",
        "login_timeout": "❌ Login timeout ({seconds}s). Aborting.",
        "searching_for": "🔍 Searching for:",
        "waiting_load": "Waiting for page to load...",
        "hiring_not_selected": "🏢 'Hiring now' not selected.",
        "no_city": "📍 No city specified.",
        "final_url": "📍 Final URL:",
        "page_of": "📄 PAGE {current} of {total}",
        "scrolling": "Scrolling page...",
        "scroll_container": "  📦 Container: {selector} (height: {height}px, visible: {visible}px)",
        "scroll_progress": "  ↓ Scroll {current}/{total} (position: {pos}px)",
        "scroll_complete": "  ✅ Scroll complete. Total scrolled: {height}px",
        "scroll_no_container": "  ⚠️ No scroll container found. Trying fallback...",
        "searching_connect": "🔍 Looking for 'Connect' buttons...",
        "found_buttons": "Found: {count}",
        "clicking_connect": "[{num}] Clicking 'Connect'...",
        "connection_sent": "✅ Connection {count} sent!",
        "sent_direct": "ℹ️ Sent directly",
        "no_buttons_left": "ℹ️ No 'Connect' buttons remaining.",
        "all_tried": "ℹ️ All visible buttons have been tried.",
        "max_failures": "⚠️ {count} consecutive failures. Stopping this page.",
        "page_stats": "📊 Page {page}: {sent} | Total: {total}",
        "limit_reached": "⚠️ Limit of {max} reached!",
        "next_page": "📄 Going to next page...",
        "next_page_ok": "✅ Next page!",
        "no_more_pages": "❌ No more pages.",
        "finished": "🎉 LinkedNektor FINISHED!",
        "finished_pages": "Pages: {pages}",
        "finished_connections": "Connections: {connections}",
        "error": "❌ Error: {msg}",
        "left_results": "⚠️ Left results page! URL: {url}",
        "going_back": "Going back to results...",
        "cant_go_back": "❌ Could not go back. Aborting this page.",
        "navigated_profile": "⚠️ Navigated to profile! Going back...",
        "unexpected_state": "⚠️ Unexpected state. Trying Escape...",
        "force_click": "Trying force click...",
        "failed_skip": "❌ Failed. Marking and skipping...",
        "btn_error": "❌ Button error idx={idx}: {msg}",
        "not_on_results": "⚠️ Not on results page. Going back...",
        "navigating_feed": "Navigating to feed...",
        "nav_error_retrying": "⚠️ Navigation interrupted. Retrying ({attempt}/{max})...",
        "waiting_page_stable": "Waiting for page to stabilize...",
        "ensuring_results": "🔍 Ensuring we are on results page...",
        "back_to_results": "✅ Back on results page.",
        "recovering_url": "🔄 Recovering results URL...",

        # Profile visit
        "collecting_profiles": "🔍 Collecting profile links from page...",
        "found_profiles": "👤 Found {count} profiles",
        "visiting_profile": "👤 [{num}/{total}] Visiting profile: {name}",
        "connect_visible": "✅ 'Connect' button visible on profile",
        "connect_in_more": "🔽 'Connect' found in 'More' menu",
        "connect_not_found": "❌ 'Connect' button not found on this profile",
        "already_connected": "ℹ️ Already connected or pending",
        "adding_note": "📝 Adding note...",
        "note_added": "✅ Note added",
        "note_failed": "⚠️ Failed to add note, sending without note",
        "returning_results": "↩️ Returning to results...",
        "profile_error": "❌ Error visiting profile: {msg}",
        "skipping_profile": "⏭️ Skipping profile (no valid URL)",

        # Filters
        "applying_hiring": "🏢 Applying 'Hiring' filter...",
        "found_selector": "✅ Found: {sel}",
        "dropdown_open": "✅ Dropdown opened",
        "typing_title": "Typing title: '{title}'...",
        "input_found": "✅ Input found: {sel}",
        "typed": "✅ '{text}' typed",
        "suggestion_selected": "✅ Suggestion: '{text}'",
        "any_title_selected": "✅ 'Any title' selected",
        "hiring_not_found": "❌ 'Hiring' filter not found.",
        "input_not_found": "❌ Input not found.",
        "applying_location": "📍 Applying location filter: {city}",
        "location_not_found": "❌ 'Locations' not found.",
        "selected_location": "✅ Selected: '{text}'",
        "looking_show_results": "Looking for 'Show results'...",
        "show_results_clicked": "✅ 'Show results' clicked!",
        "show_results_not_found": "⚠️ 'Show results' button not found.",

        # LinkedIn elements (EN)
        "li_connect": "Connect",
        "li_connect_alt": "Conectar",
        "li_send_no_note": "Send without a note",
        "li_send_now": "Send now",
        "li_send": "Send",
        "li_hiring": "Hiring",
        "li_any_title": "Any title",
        "li_locations": "Locations",
        "li_show_results": "Show results",
        "li_show_results_alt": "Apply",
        "li_next": "Next",
        "li_hiring_input": "Hiring for",
        "li_add_location": "Add a location",
        "li_more": "More",
        "li_add_note": "Add a note",
    },
}

# Current language (default: English)
current_lang = "en"


def t(key, **kwargs):
    """Returns the translation for the key in the current language."""
    text = TRANSLATIONS.get(current_lang, TRANSLATIONS["en"]).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text


# ===== AUTOMATION FUNCTIONS =====

def human_delay(min_time=2.0, max_time=4.0):
    time.sleep(random.uniform(min_time, max_time))


def is_logged_in(page):
    url = page.url.lower()
    login_indicators = ["login", "checkpoint", "authwall", "signup"]
    for indicator in login_indicators:
        if indicator in url:
            return False
    logged_indicators = ["/feed", "/mynetwork", "/messaging", "/notifications", "/search"]
    for indicator in logged_indicators:
        if indicator in url:
            return True
    try:
        nav = page.locator("nav, .global-nav, #global-nav")
        if nav.count() > 0:
            return True
    except:
        pass
    return False


def wait_for_login(page, timeout_seconds=300):
    print(t("not_logged_in"))
    start_time = time.time()
    last_print = 0
    while True:
        elapsed = int(time.time() - start_time)
        if elapsed - last_print >= 10:
            print(f"  {t('waiting_login', seconds=elapsed)}")
            last_print = elapsed
        if elapsed >= timeout_seconds:
            print(t("login_timeout", seconds=timeout_seconds))
            return False
        try:
            if is_logged_in(page):
                print(f"  {t('login_detected')}")
                return True
        except:
            pass
        time.sleep(3)


def safe_goto(page, url, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            return True
        except Exception as e:
            error_msg = str(e)
            if "interrupted" in error_msg.lower() or "navigation" in error_msg.lower():
                if attempt < max_retries:
                    print(f"  {t('nav_error_retrying', attempt=attempt, max=max_retries)}")
                    time.sleep(5)
                    try:
                        page.wait_for_load_state("domcontentloaded", timeout=10000)
                    except:
                        pass
                    if url.split("?")[0] in page.url:
                        return True
                else:
                    try:
                        page.wait_for_load_state("domcontentloaded", timeout=10000)
                    except:
                        pass
                    if "linkedin.com" in page.url:
                        return True
                    raise
            else:
                raise
    return False


def is_on_results_page(page):
    return "/search/results/" in page.url


def ensure_on_results(page, search_url=None):
    if is_on_results_page(page):
        return True
    print(f"  {t('ensuring_results')}")
    current = page.url
    print(f"  {t('left_results', url=current[:80])}")
    try:
        page.go_back()
        human_delay(3, 5)
        if is_on_results_page(page):
            print(f"  {t('back_to_results')}")
            return True
    except:
        pass
    if search_url:
        print(f"  {t('recovering_url')}")
        try:
            safe_goto(page, search_url)
            human_delay(3, 5)
            if is_on_results_page(page):
                print(f"  {t('back_to_results')}")
                return True
        except:
            pass
    for _ in range(3):
        try:
            page.go_back()
            human_delay(2, 3)
            if is_on_results_page(page):
                print(f"  {t('back_to_results')}")
                return True
        except:
            pass
    print(f"  {t('cant_go_back')}")
    return False


def dismiss_overlays(page):
    try:
        page.keyboard.press("Escape")
        time.sleep(0.5)
        page.keyboard.press("Escape")
        time.sleep(0.5)
    except:
        pass


def find_scroll_container(page):
    result = page.evaluate("""() => {
        const candidates = document.querySelectorAll('div, main, section');
        let best = null;
        let bestHeight = 0;
        for (const el of candidates) {
            const style = window.getComputedStyle(el);
            const overflowY = style.overflowY;
            const isScrollable = (overflowY === 'auto' || overflowY === 'scroll');
            if (isScrollable && el.scrollHeight > el.clientHeight) {
                const diff = el.scrollHeight - el.clientHeight;
                if (diff > bestHeight) {
                    bestHeight = diff;
                    best = el;
                }
            }
        }
        if (best) {
            if (best.id) return { selector: '#' + best.id, scrollHeight: best.scrollHeight, clientHeight: best.clientHeight };
            if (best.className) {
                const classes = best.className.trim().split(/\\s+/).slice(0, 3).join('.');
                return { selector: best.tagName.toLowerCase() + '.' + classes, scrollHeight: best.scrollHeight, clientHeight: best.clientHeight };
            }
            return { selector: best.tagName.toLowerCase(), scrollHeight: best.scrollHeight, clientHeight: best.clientHeight };
        }
        const docEl = document.documentElement;
        const body = document.body;
        if (docEl.scrollHeight > docEl.clientHeight) {
            return { selector: 'documentElement', scrollHeight: docEl.scrollHeight, clientHeight: docEl.clientHeight };
        }
        if (body.scrollHeight > body.clientHeight) {
            return { selector: 'body', scrollHeight: body.scrollHeight, clientHeight: body.clientHeight };
        }
        const allScrollable = [];
        for (const el of document.querySelectorAll('*')) {
            if (el.scrollHeight > el.clientHeight + 50) {
                const tag = el.tagName.toLowerCase();
                const id = el.id ? '#' + el.id : '';
                const cls = el.className ? '.' + el.className.trim().split(/\\s+/).slice(0, 2).join('.') : '';
                allScrollable.push({ desc: tag + id + cls, scrollHeight: el.scrollHeight, clientHeight: el.clientHeight });
            }
        }
        return { selector: null, scrollHeight: 0, clientHeight: 0, candidates: allScrollable.slice(0, 10) };
    }""")
    return result


def scroll_page_fully(page, scroll_steps=8):
    print(t("scrolling"))
    container_info = find_scroll_container(page)
    selector = container_info.get("selector")
    scroll_height = container_info.get("scrollHeight", 0)
    client_height = container_info.get("clientHeight", 0)

    if selector and selector not in ("documentElement", "body", None):
        print(t("scroll_container", selector=selector, height=scroll_height, visible=client_height))
        scroll_amount = client_height * 0.7
        for i in range(scroll_steps):
            target = int(scroll_amount * (i + 1))
            pos = page.evaluate(f"""() => {{
                const el = document.querySelector('{selector}');
                if (el) {{ el.scrollTop = {target}; return el.scrollTop; }}
                return -1;
            }}""")
            time.sleep(random.uniform(1.0, 2.0))
            print(t("scroll_progress", current=i+1, total=scroll_steps, pos=int(pos)))
            new_height = page.evaluate(f"""() => {{
                const el = document.querySelector('{selector}');
                return el ? el.scrollHeight : 0;
            }}""")
            if new_height > scroll_height:
                scroll_height = new_height
        page.evaluate(f"""() => {{
            const el = document.querySelector('{selector}');
            if (el) el.scrollTop = el.scrollHeight;
        }}""")
        time.sleep(2)
        page.evaluate(f"""() => {{
            const el = document.querySelector('{selector}');
            if (el) el.scrollTop = 0;
        }}""")
        time.sleep(1.5)
        for i in range(scroll_steps):
            target = int(scroll_amount * (i + 1))
            page.evaluate(f"""() => {{
                const el = document.querySelector('{selector}');
                if (el) el.scrollTop = {target};
            }}""")
            time.sleep(random.uniform(0.6, 1.2))
        final_pos = page.evaluate(f"""() => {{
            const el = document.querySelector('{selector}');
            if (el) {{ el.scrollTop = el.scrollHeight; return el.scrollTop; }}
            return 0;
        }}""")
        time.sleep(1.5)
        page.evaluate(f"""() => {{
            const el = document.querySelector('{selector}');
            if (el) el.scrollTop = 0;
        }}""")
        time.sleep(1.5)
        print(t("scroll_complete", height=int(final_pos)))
        return True
    elif selector in ("documentElement", "body"):
        print(t("scroll_container", selector=selector, height=scroll_height, visible=client_height))
        scroll_amount = client_height * 0.7
        for i in range(scroll_steps):
            target = int(scroll_amount * (i + 1))
            page.evaluate(f"window.scrollTo(0, {target})")
            time.sleep(random.uniform(1.0, 2.0))
            pos = page.evaluate("window.pageYOffset || document.documentElement.scrollTop")
            print(t("scroll_progress", current=i+1, total=scroll_steps, pos=int(pos)))
        page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
        time.sleep(2)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1.5)
        for i in range(scroll_steps):
            target = int(scroll_amount * (i + 1))
            page.evaluate(f"window.scrollTo(0, {target})")
            time.sleep(random.uniform(0.6, 1.2))
        page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
        time.sleep(1.5)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1.5)
        print(t("scroll_complete", height=scroll_height))
        return True
    else:
        print(t("scroll_no_container"))
        if container_info.get("candidates"):
            print("  Candidates found:")
            for c in container_info["candidates"][:5]:
                print(f"    {c['desc']} (scroll: {c['scrollHeight']}px, visible: {c['clientHeight']}px)")
        print("  🖱️ Using mouse wheel fallback...")
        try:
            viewport = page.viewport_size
            if viewport:
                cx = viewport["width"] // 2
                cy = viewport["height"] // 2
            else:
                cx, cy = 600, 400
        except:
            cx, cy = 600, 400
        page.mouse.move(cx, cy)
        time.sleep(0.5)
        for i in range(scroll_steps * 3):
            page.mouse.wheel(0, 500)
            time.sleep(random.uniform(0.5, 1.0))
            if (i + 1) % 4 == 0:
                print(f"  ↓ Wheel scroll {i+1}/{scroll_steps * 3}")
        time.sleep(2)
        for i in range(scroll_steps * 3):
            page.mouse.wheel(0, -500)
            time.sleep(random.uniform(0.3, 0.5))
        time.sleep(1)
        for i in range(scroll_steps * 3):
            page.mouse.wheel(0, 500)
            time.sleep(random.uniform(0.4, 0.8))
        time.sleep(1.5)
        for i in range(scroll_steps * 3):
            page.mouse.wheel(0, -500)
            time.sleep(random.uniform(0.2, 0.4))
        time.sleep(1.5)
        print(t("scroll_complete", height=0))
        return True


def click_show_results(page):
    print(f"  {t('looking_show_results')}")
    human_delay(1, 2)
    selectors = []
    for text in [
        t("li_show_results"), t("li_show_results_alt"),
        "Show results", "Apply",
        "Exibir resultados", "Mostrar resultados",
    ]:
        selectors.append(f"span:text-is('{text}')")
        selectors.append(f"button:has-text('{text}')")
    selectors.append("button:has-text('results')")
    selectors.append("button:has-text('resultados')")
    selectors.append("text=Show results")
    selectors.append("text=Exibir resultados")
    seen = set()
    for selector in selectors:
        if selector in seen:
            continue
        seen.add(selector)
        loc = page.locator(selector)
        for i in range(loc.count()):
            try:
                if loc.nth(i).is_visible():
                    loc.nth(i).click(timeout=5000)
                    print(f"  {t('show_results_clicked')}")
                    human_delay(4, 6)
                    return True
            except:
                pass
    print(f"  {t('show_results_not_found')}")
    return False


def apply_hiring_filter(page, title):
    print(f"\n{t('applying_hiring')}")
    if not is_on_results_page(page):
        print(f"  {t('not_on_results')}")
        return False
    hiring_btn = None
    hiring_terms = [t("li_hiring"), "Hiring", "Contratando já", "Contratando"]
    for term in hiring_terms:
        for prefix in ["button:has-text", "span:text-is", "label:text-is"]:
            selector = f"{prefix}('{term}')"
            loc = page.locator(selector)
            for i in range(loc.count()):
                try:
                    if loc.nth(i).is_visible():
                        hiring_btn = loc.nth(i)
                        print(f"  {t('found_selector', sel=selector)}")
                        break
                except:
                    pass
                if hiring_btn:
                    break
            if hiring_btn:
                break
        if hiring_btn:
            break
    if not hiring_btn:
        for term in hiring_terms:
            loc = page.locator(f"text={term}")
            for i in range(loc.count()):
                try:
                    if loc.nth(i).is_visible():
                        hiring_btn = loc.nth(i)
                        break
                except:
                    pass
            if hiring_btn:
                break
    if not hiring_btn:
        print(f"  {t('hiring_not_found')}")
        return False
    hiring_btn.click(timeout=5000)
    human_delay(2, 3)
    print(f"  {t('dropdown_open')}")
    if title:
        print(f"  {t('typing_title', title=title)}")
        hiring_input = None
        input_placeholders = [
            t("li_hiring_input"), "Hiring for", "title",
            "Contratando para cargo", "Contratando", "cargo",
        ]
        for ph in input_placeholders:
            selector = f"input[placeholder*='{ph}']"
            loc = page.locator(selector)
            for i in range(loc.count()):
                try:
                    if loc.nth(i).is_visible():
                        hiring_input = loc.nth(i)
                        print(f"  {t('input_found', sel=selector)}")
                        break
                except:
                    pass
            if hiring_input:
                break
        if hiring_input:
            hiring_input.click(timeout=5000)
            human_delay(0.5, 1)
            hiring_input.fill("")
            human_delay(0.3, 0.5)
            for char in title:
                hiring_input.type(char, delay=random.randint(50, 150))
            print(f"  {t('typed', text=title)}")
            human_delay(2, 4)
            selected = False
            for sel in ["div[role='option']", "li[role='option']"]:
                sug = page.locator(sel)
                if sug.count() > 0:
                    for j in range(sug.count()):
                        try:
                            if sug.nth(j).is_visible():
                                txt = sug.nth(j).inner_text(timeout=2000).strip().split("\n")[0]
                                sug.nth(j).click(timeout=5000)
                                print(f"  {t('suggestion_selected', text=txt)}")
                                selected = True
                                human_delay(1, 2)
                                break
                        except:
                            pass
                if selected:
                    break
        else:
            print(f"  {t('input_not_found')}")
    else:
        any_terms = [t("li_any_title"), "Any title", "Qualquer cargo"]
        any_job = None
        for term in any_terms:
            for prefix in ["label:has-text", "text="]:
                selector = f"{prefix}('{term}')" if "text=" not in prefix else f"{prefix}{term}"
                loc = page.locator(selector)
                for i in range(loc.count()):
                    try:
                        if loc.nth(i).is_visible():
                            any_job = loc.nth(i)
                            break
                    except:
                        pass
                if any_job:
                    break
            if any_job:
                break
        if any_job:
            any_job.click(timeout=5000)
            print(f"  {t('any_title_selected')}")
            human_delay(1, 2)
    human_delay(1, 2)
    result = click_show_results(page)
    if not result:
        page.keyboard.press("Escape")
        human_delay(2, 3)
    return True


def apply_location_filter(page, city):
    print(f"\n{t('applying_location', city=city)}")
    if not is_on_results_page(page):
        print(f"  {t('not_on_results')}")
        return False
    location_btn = None
    loc_terms = [t("li_locations"), "Locations", "Localidades"]
    for term in loc_terms:
        for prefix in ["label:text-is", "button:has-text", "span:text-is"]:
            selector = f"{prefix}('{term}')"
            loc = page.locator(selector)
            if loc.count() > 0 and loc.first.is_visible():
                location_btn = loc.first
                break
        if location_btn:
            break
    if not location_btn:
        for term in loc_terms:
            loc = page.locator(f"text={term}")
            for i in range(loc.count()):
                try:
                    if loc.nth(i).is_visible():
                        location_btn = loc.nth(i)
                        break
                except:
                    pass
            if location_btn:
                break
    if not location_btn:
        print(f"  {t('location_not_found')}")
        return False
    location_btn.click(timeout=5000)
    human_delay(2, 3)
    print(f"  {t('dropdown_open')}")
    search_input = None
    loc_placeholders = [
        t("li_add_location"), "Add a location", "location",
        "Adicionar localidade", "localidade", "Adicionar",
    ]
    for ph in loc_placeholders:
        selector = f"input[placeholder*='{ph}']"
        loc2 = page.locator(selector)
        for i in range(loc2.count()):
            try:
                if loc2.nth(i).is_visible():
                    search_input = loc2.nth(i)
                    break
            except:
                pass
        if search_input:
            break
    if not search_input:
        print(f"  {t('input_not_found')}")
        page.keyboard.press("Escape")
        return False
    search_input.click(timeout=5000)
    human_delay(0.5, 1)
    search_input.fill("")
    for char in city:
        search_input.type(char, delay=random.randint(50, 150))
    print(f"  {t('typed', text=city)}")
    human_delay(2, 4)
    for sel in ["div[role='option']", "li[role='option']"]:
        sug = page.locator(sel)
        if sug.count() > 0 and sug.first.is_visible():
            txt = sug.first.inner_text(timeout=2000).strip().split("\n")[0]
            sug.first.click(timeout=5000)
            print(f"  {t('selected_location', text=txt)}")
            human_delay(2, 3)
            break
    click_show_results(page)
    return True


def go_to_next_page(page):
    print(f"\n{t('next_page')}")
    page.evaluate("""() => {
        const candidates = document.querySelectorAll('div, main, section');
        for (const el of candidates) {
            const style = window.getComputedStyle(el);
            if ((style.overflowY === 'auto' || style.overflowY === 'scroll') &&
                el.scrollHeight > el.clientHeight) {
                el.scrollTop = el.scrollHeight;
            }
        }
        window.scrollTo(0, document.documentElement.scrollHeight);
    }""")
    time.sleep(2)
    try:
        viewport = page.viewport_size
        cx = (viewport["width"] // 2) if viewport else 600
        cy = (viewport["height"] // 2) if viewport else 400
        page.mouse.move(cx, cy)
        for _ in range(10):
            page.mouse.wheel(0, 800)
            time.sleep(0.3)
    except:
        pass
    time.sleep(1)
    next_btn = None
    next_terms = [t("li_next"), "Next", "Próxima"]
    for term in next_terms:
        for prefix in ["button:has-text", "span:text-is"]:
            selector = f"{prefix}('{term}')"
            loc = page.locator(selector)
            if loc.count() > 0 and loc.first.is_visible():
                next_btn = loc.first
                break
        if next_btn:
            break
    if not next_btn:
        for label in ["Next", "Próxima", "Avançar"]:
            loc = page.locator(f"button[aria-label='{label}']")
            if loc.count() > 0 and loc.first.is_visible():
                next_btn = loc.first
                break
    if not next_btn:
        try:
            pagination = page.locator("ul.artdeco-pagination__pages li")
            if pagination.count() > 0:
                for i in range(pagination.count()):
                    li = pagination.nth(i)
                    if "active" in (li.get_attribute("class") or ""):
                        if i + 1 < pagination.count():
                            btn = pagination.nth(i + 1).locator("button")
                            if btn.count() > 0:
                                next_btn = btn.first
                        break
        except:
            pass
    if next_btn:
        try:
            next_btn.scroll_into_view_if_needed(timeout=5000)
        except:
            pass
        human_delay(1, 2)
        next_btn.click(timeout=5000)
        print(f"  {t('next_page_ok')}")
        human_delay(4, 7)
        return True
    else:
        print(f"  {t('no_more_pages')}")
        return False


def collect_profile_links(page):
    """Collects all profile URLs from the current search results page."""
    print(f"\n{t('collecting_profiles')}")

    profiles = page.evaluate("""() => {
        const results = [];
        // LinkedIn search results: each person card has a link to their profile
        const linkSelectors = [
            'a.app-aware-link[href*="/in/"]',
            'a[href*="/in/"]',
            '.entity-result__title-text a',
            '.reusable-search__result-container a[href*="/in/"]',
            'span.entity-result__title-text a',
        ];

        const seen = new Set();

        for (const selector of linkSelectors) {
            const links = document.querySelectorAll(selector);
            for (const link of links) {
                const href = link.href;
                if (href && href.includes('/in/') && !seen.has(href.split('?')[0])) {
                    const cleanUrl = href.split('?')[0];
                    seen.add(cleanUrl);

                    // Get the name from the link text or nearby elements
                    let name = link.textContent.trim().split('\\n')[0].trim();
                    if (!name || name.length < 2) {
                        const span = link.querySelector('span[aria-hidden="true"]');
                        if (span) name = span.textContent.trim();
                    }

                    // Filter out non-person links
                    if (cleanUrl.match(/linkedin\\.com\\/in\\/[\\w-]+/)) {
                        results.push({
                            url: cleanUrl,
                            name: name || 'Unknown'
                        });
                    }
                }
            }
            if (results.length > 0) break;
        }

        return results;
    }""")

    # Deduplicate by URL
    seen_urls = set()
    unique_profiles = []
    for p in profiles:
        url = p["url"].rstrip("/")
        if url not in seen_urls:
            seen_urls.add(url)
            unique_profiles.append(p)

    print(f"  {t('found_profiles', count=len(unique_profiles))}")
    return unique_profiles


def find_connect_button_on_profile(page):
    """
    Finds and clicks the Connect button on a LinkedIn profile page.
    Handles two cases:
    1. Connect button is directly visible
    2. Connect button is hidden inside the "More" dropdown menu

    Returns: 'found' if Connect button was clicked, 'already' if already connected, 'not_found' otherwise
    """
    human_delay(2, 3)

    # Check if already connected or pending
    already_indicators = [
        "Pendente", "Pending",
        "Mensagem", "Message",  # If "Message" is primary, they're already connected
    ]

    # Check primary action buttons
    for indicator in already_indicators:
        # "Message" as primary button (not inside More) means already connected
        if indicator in ["Mensagem", "Message"]:
            loc = page.locator(f"button.pvs-profile-actions__action:has-text('{indicator}')")
            if loc.count() > 0:
                try:
                    if loc.first.is_visible():
                        # Check if there's NO connect button visible - means already connected
                        connect_terms = [t("li_connect"), t("li_connect_alt"), "Connect", "Conectar"]
                        has_connect = False
                        for ct in connect_terms:
                            cl = page.locator(f"button:has-text('{ct}')")
                            for ci in range(cl.count()):
                                try:
                                    if cl.nth(ci).is_visible():
                                        has_connect = True
                                        break
                                except:
                                    pass
                            if has_connect:
                                break
                        if not has_connect:
                            pass  # Don't return yet, check More menu
                except:
                    pass
        else:
            loc = page.locator(f"button:has-text('{indicator}')")
            if loc.count() > 0:
                try:
                    if loc.first.is_visible():
                        print(f"  {t('already_connected')}")
                        return "already"
                except:
                    pass

    # Case 1: Connect button directly visible on the profile
    connect_terms = [t("li_connect"), t("li_connect_alt"), "Connect", "Conectar"]
    seen_terms = set()
    unique_connect = []
    for ct in connect_terms:
        if ct not in seen_terms:
            seen_terms.add(ct)
            unique_connect.append(ct)

    for term in unique_connect:
        # Try multiple selectors for visible Connect button
        selectors = [
            f"button:has-text('{term}')",
            f"button > span:text-is('{term}')",
        ]
        for sel in selectors:
            loc = page.locator(sel)
            for i in range(loc.count()):
                try:
                    el = loc.nth(i)
                    if el.is_visible(timeout=2000):
                        # Make sure this is a primary action button, not in a dropdown
                        tag = el.evaluate("el => el.tagName.toLowerCase()")
                        if tag == "span":
                            # Click parent button
                            parent_btn = el.locator("xpath=..")
                            if parent_btn.count() > 0:
                                parent_btn.first.click(timeout=5000)
                            else:
                                el.click(timeout=5000)
                        else:
                            el.click(timeout=5000)
                        print(f"  {t('connect_visible')}")
                        return "found"
                except:
                    continue

    # Case 2: Connect hidden in "More" menu
    more_terms = [t("li_more"), "More", "Mais"]
    more_btn = None
    for mterm in more_terms:
        selectors = [
            f"button:has-text('{mterm}')",
            f"div.artdeco-dropdown > button:has-text('{mterm}')",
            f"button[aria-label='{mterm}']",
        ]
        for sel in selectors:
            loc = page.locator(sel)
            for i in range(loc.count()):
                try:
                    el = loc.nth(i)
                    if el.is_visible(timeout=2000):
                        more_btn = el
                        break
                except:
                    pass
            if more_btn:
                break
        if more_btn:
            break

    if more_btn:
        try:
            more_btn.click(timeout=5000)
            human_delay(1, 2)

            # Now look for Connect inside the dropdown
            for term in unique_connect:
                dropdown_selectors = [
                    f"div[role='listbox'] span:text-is('{term}')",
                    f".artdeco-dropdown__content span:text-is('{term}')",
                    f"div.artdeco-dropdown__content-inner span:text-is('{term}')",
                    f"div[role='menu'] span:text-is('{term}')",
                    f"ul[role='menu'] span:text-is('{term}')",
                    f"div.pvs-overflow-actions-dropdown__content span:text-is('{term}')",
                    f"span:text-is('{term}')",
                ]
                for sel in dropdown_selectors:
                    loc = page.locator(sel)
                    for i in range(loc.count()):
                        try:
                            el = loc.nth(i)
                            if el.is_visible(timeout=2000):
                                # Click the parent list item or the element itself
                                parent_item = el.locator("xpath=ancestor::div[contains(@class,'artdeco-dropdown__item') or @role='menuitem' or contains(@class,'dropdown')]")
                                if parent_item.count() > 0:
                                    parent_item.first.click(timeout=5000)
                                else:
                                    el.click(timeout=5000)
                                print(f"  {t('connect_in_more')}")
                                return "found"
                        except:
                            continue
        except Exception as e:
            print(f"  ⚠️ More menu error: {str(e)[:50]}")

        # Close dropdown if Connect not found
        try:
            page.keyboard.press("Escape")
            time.sleep(0.5)
        except:
            pass

    print(f"  {t('connect_not_found')}")
    return "not_found"


def handle_connection_dialog(page, note_text=""):
    """
    Handles the connection invitation dialog.
    If note_text is provided, clicks "Add a note" and types the note.
    Otherwise sends without note.
    Returns True if invitation was sent successfully.
    """
    human_delay(1.5, 3)

    # Check if a dialog/modal appeared
    dialog_visible = False
    dialog_selectors = [
        "div[role='dialog']",
        "div.artdeco-modal",
        "div.send-invite",
        "div[data-test-modal]",
    ]
    for ds in dialog_selectors:
        loc = page.locator(ds)
        if loc.count() > 0:
            try:
                if loc.first.is_visible(timeout=3000):
                    dialog_visible = True
                    break
            except:
                pass

    if not dialog_visible:
        # Maybe it was sent directly without dialog
        return True

    # If we have a note, click "Add a note" first
    if note_text:
        print(f"    {t('adding_note')}")
        add_note_terms = [
            t("li_add_note"), "Add a note", "Adicionar nota",
            "Add note", "Adicionar uma nota",
        ]

        note_clicked = False
        for term in add_note_terms:
            selectors = [
                f"button:has-text('{term}')",
                f"button > span:text-is('{term}')",
                f"span:text-is('{term}')",
            ]
            for sel in selectors:
                loc = page.locator(sel)
                for i in range(loc.count()):
                    try:
                        el = loc.nth(i)
                        if el.is_visible(timeout=2000):
                            el.click(timeout=5000)
                            note_clicked = True
                            break
                    except:
                        continue
                if note_clicked:
                    break
            if note_clicked:
                break

        if note_clicked:
            human_delay(1, 2)

            # Find the note textarea and type the note
            textarea_selectors = [
                "textarea[name='message']",
                "textarea#custom-message",
                "textarea.connect-button-send-invite__custom-message",
                "textarea",
            ]

            textarea = None
            for ts in textarea_selectors:
                loc = page.locator(ts)
                for i in range(loc.count()):
                    try:
                        el = loc.nth(i)
                        if el.is_visible(timeout=2000):
                            textarea = el
                            break
                    except:
                        pass
                if textarea:
                    break

            if textarea:
                textarea.click(timeout=3000)
                human_delay(0.3, 0.5)
                textarea.fill("")
                human_delay(0.3, 0.5)

                # Type character by character for human-like behavior
                for char in note_text:
                    textarea.type(char, delay=random.randint(30, 80))

                print(f"    {t('note_added')}")
                human_delay(1, 2)
            else:
                print(f"    {t('note_failed')}")
        else:
            print(f"    {t('note_failed')}")

    # Now click Send / Send now / Send without a note
    send_labels = [
        t("li_send_no_note"),
        "Send without a note", "Enviar sem nota",
        t("li_send_now"),
        "Send now", "Enviar agora",
    ]

    # If we added a note, prioritize "Send" / "Send now"
    if note_text:
        send_labels = [
            t("li_send_now"), "Send now", "Enviar agora",
            t("li_send"), "Send", "Enviar",
            t("li_send_no_note"),
            "Send without a note", "Enviar sem nota",
        ]

    seen = set()
    unique_labels = []
    for lbl in send_labels:
        if lbl not in seen:
            seen.add(lbl)
            unique_labels.append(lbl)

    for label in unique_labels:
        loc = page.get_by_role("button", name=label)
        if loc.count() > 0:
            try:
                loc.first.click(timeout=5000)
                return True
            except:
                pass
        loc2 = page.locator(f"button:has-text('{label}')")
        if loc2.count() > 0:
            try:
                loc2.first.click(timeout=5000)
                return True
            except:
                pass

    # Generic Send
    send_generic = [t("li_send"), "Send", "Enviar"]
    seen2 = set()
    unique_generic = []
    for lbl in send_generic:
        if lbl not in seen2:
            seen2.add(lbl)
            unique_generic.append(lbl)

    for label in unique_generic:
        loc = page.get_by_role("button", name=label, exact=True)
        if loc.count() > 0:
            try:
                loc.first.click(timeout=5000)
                return True
            except:
                pass

    # Last resort
    loc3 = page.locator(
        "button:has-text('Send'), "
        "button:has-text('Enviar')"
    )
    if loc3.count() > 0:
        try:
            loc3.first.click(timeout=5000)
            return True
        except:
            pass

    return False


def process_page_via_profiles(page, max_left, note_text="", search_url=None):
    """
    New approach: collects profile links, visits each one,
    finds Connect button (visible or in More menu), sends invitation with optional note.
    """
    # Collect all profile links from the results page
    profiles = collect_profile_links(page)

    if not profiles:
        print(f"  {t('no_buttons_left')}")
        return 0

    count_sent = 0
    consecutive_failures = 0
    max_failures_limit = 5

    for idx, profile in enumerate(profiles):
        if count_sent >= max_left:
            print(f"\n{t('limit_reached', max=max_left)}")
            break

        if consecutive_failures >= max_failures_limit:
            print(f"  {t('max_failures', count=max_failures_limit)}")
            break

        profile_url = profile["url"]
        profile_name = profile["name"][:40]

        if not profile_url or "/in/" not in profile_url:
            print(f"  {t('skipping_profile')}")
            continue

        print(f"\n  {t('visiting_profile', num=idx+1, total=len(profiles), name=profile_name)}")

        try:
            # Navigate to the profile
            safe_goto(page, profile_url)
            human_delay(3, 5)

            # Wait for page to load
            try:
                page.wait_for_load_state("domcontentloaded", timeout=15000)
            except:
                pass
            human_delay(1, 2)

            # Find and click Connect
            result = find_connect_button_on_profile(page)

            if result == "found":
                # Handle the connection dialog (with optional note)
                if handle_connection_dialog(page, note_text):
                    count_sent += 1
                    print(f"  {t('connection_sent', count=count_sent)}")
                    consecutive_failures = 0
                else:
                    print(f"  {t('unexpected_state')}")
                    dismiss_overlays(page)
                    consecutive_failures += 1

                human_delay(2, 4)

            elif result == "already":
                # Already connected, just skip
                consecutive_failures = 0

            else:
                # Not found
                consecutive_failures += 1

        except Exception as e:
            print(f"  {t('profile_error', msg=str(e)[:60])}")
            consecutive_failures += 1
            dismiss_overlays(page)

        # Return to search results
        print(f"  {t('returning_results')}")
        try:
            if search_url:
                safe_goto(page, search_url)
            else:
                page.go_back()
            human_delay(3, 5)

            if not is_on_results_page(page):
                if search_url:
                    safe_goto(page, search_url)
                    human_delay(3, 5)
        except:
            if search_url:
                try:
                    safe_goto(page, search_url)
                    human_delay(3, 5)
                except:
                    pass

        human_delay(1, 3)

    return count_sent


def run_bot(city, job, title, num_pages, hiring, note_text=""):
    keyword = urllib.parse.quote(job)
    user_data_dir = os.path.join(
        os.path.expanduser("~"), "linkednektor_profile"
    )

    try:
        with sync_playwright() as p:
            print(t("opening_browser"))
            context = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,
                channel="chrome",
                args=[
                    "--start-maximized",
                    "--disable-blink-features=AutomationControlled",
                ],
                no_viewport=True,
                locale="en-US" if current_lang == "en" else "pt-BR",
            )

            page = context.pages[0] if context.pages else context.new_page()

            print(t("accessing_linkedin"))

            try:
                page.goto(
                    "https://www.linkedin.com/feed/",
                    wait_until="domcontentloaded",
                    timeout=30000,
                )
            except Exception:
                print(f"  {t('waiting_page_stable')}")
                try:
                    page.wait_for_load_state("domcontentloaded", timeout=15000)
                except:
                    pass

            human_delay(3, 5)

            if not is_logged_in(page):
                login_success = wait_for_login(page, timeout_seconds=300)
                if not login_success:
                    print(t("login_timeout", seconds=300))
                    context.close()
                    return

                human_delay(2, 3)
                print(f"  {t('navigating_feed')}")
                safe_goto(page, "https://www.linkedin.com/feed/")
                human_delay(3, 5)

                if not is_logged_in(page):
                    login_success = wait_for_login(page, timeout_seconds=120)
                    if not login_success:
                        context.close()
                        return
                    human_delay(2, 3)
                    safe_goto(page, "https://www.linkedin.com/feed/")
                    human_delay(3, 5)

            search_url = (
                f"https://www.linkedin.com/search/results/people/"
                f"?keywords={keyword}&origin=SWITCH_SEARCH_VERTICAL"
            )
            print(f"\n{t('searching_for')} {job}")
            safe_goto(page, search_url)
            print(t("waiting_load"))
            human_delay(5, 8)

            dismiss_overlays(page)
            human_delay(1, 2)

            if not ensure_on_results(page, search_url):
                print(f"  {t('cant_go_back')}")
                context.close()
                return

            current_search_url = page.url

            # --- FILTERS ---
            if hiring:
                if is_on_results_page(page):
                    apply_hiring_filter(page, title)
                    human_delay(2, 3)
                    dismiss_overlays(page)
                    human_delay(1, 2)
                    if is_on_results_page(page):
                        current_search_url = page.url
                else:
                    ensure_on_results(page, current_search_url)
            else:
                print(f"\n{t('hiring_not_selected')}")

            if city:
                if not is_on_results_page(page):
                    ensure_on_results(page, current_search_url)
                    human_delay(2, 3)

                if is_on_results_page(page):
                    apply_location_filter(page, city)
                    human_delay(2, 3)
                    dismiss_overlays(page)
                    human_delay(1, 2)
                    if is_on_results_page(page):
                        current_search_url = page.url
            else:
                print(f"\n{t('no_city')}")

            if not is_on_results_page(page):
                ensure_on_results(page, current_search_url)
                human_delay(2, 3)

            print(f"\n{t('final_url')} {page.url}")
            dismiss_overlays(page)
            human_delay(2, 3)

            if is_on_results_page(page):
                current_search_url = page.url

            # --- PAGE LOOP ---
            total_sent = 0
            max_per_run = 50

            for page_num in range(1, num_pages + 1):
                print(f"\n{'=' * 50}")
                print(t("page_of", current=page_num, total=num_pages))
                print(f"{'=' * 50}")

                if not is_on_results_page(page):
                    if not ensure_on_results(page, current_search_url):
                        break
                    human_delay(2, 3)

                dismiss_overlays(page)
                human_delay(1, 2)

                scroll_page_fully(page, scroll_steps=8)
                human_delay(2, 3)

                max_left = max_per_run - total_sent
                if max_left <= 0:
                    print(f"\n{t('limit_reached', max=max_per_run)}")
                    break

                # Build the current page URL for returning after profile visits
                current_search_url = page.url

                sent = process_page_via_profiles(
                    page, max_left,
                    note_text=note_text,
                    search_url=current_search_url
                )
                total_sent += sent
                print(
                    f"\n  {t('page_stats', page=page_num, sent=sent, total=total_sent)}"
                )

                if page_num < num_pages:
                    if not is_on_results_page(page):
                        if not ensure_on_results(page, current_search_url):
                            break
                        human_delay(2, 3)

                    if not go_to_next_page(page):
                        break

            print(f"\n{'=' * 50}")
            print(t("finished"))
            print(f"   {t('finished_pages', pages=page_num)}")
            print(f"   {t('finished_connections', connections=total_sent)}")
            print(f"{'=' * 50}")

            context.close()

    except Exception as e:
        print(f"\n{t('error', msg=str(e))}")


# ===== GRAPHICAL USER INTERFACE =====

def update_gui_language():
    root.title(t("window_title"))
    label_search.config(text=t("label_search"))
    label_city.config(text=t("label_city"))
    label_title.config(text=t("label_title"))
    label_pages.config(text=t("label_pages"))
    hiring_check.config(text=t("checkbox_hiring"))
    start_button.config(text=t("btn_start"))
    lang_button.config(text=t("btn_language"))


def toggle_language():
    global current_lang
    current_lang = "pt" if current_lang == "en" else "en"
    update_gui_language()


def start_bot():
    city = city_entry.get().strip()
    job = job_entry.get().strip()
    title = title_entry.get().strip()
    hiring = hiring_var.get()

    try:
        pages = int(pages_entry.get().strip())
        pages = max(1, min(20, pages))
    except:
        pages = 1

    if not job:
        messagebox.showwarning(t("warning_title"), t("warning_fill"))
        return

    # --- Note popup before starting ---
    note_text = simpledialog.askstring(
        t("note_popup_title"),
        t("note_popup_msg"),
        parent=root
    )
    if note_text is None:
        # User cancelled the dialog — abort
        return
    note_text = note_text.strip()

    if note_text:
        print(f"  {t('note_set', note=note_text[:50])}")
    else:
        print(f"  {t('note_empty')}")

    print(f"\n{t('starting')}")
    print(f"  {t('search_label')}: {job}")
    print(f"  {t('city_label')}: {city if city else t('none')}")
    print(f"  {t('title_label')}: {title if title else t('any')}")
    print(f"  {t('hiring_label')}: {t('yes') if hiring else t('no')}")
    print(f"  {t('pages_label')}: {pages}")
    print(f"  {t('note_label')}: {note_text if note_text else t('none')}")

    thread = threading.Thread(
        target=run_bot, args=(city, job, title, pages, hiring, note_text)
    )
    thread.daemon = True
    thread.start()


root = tk.Tk()
root.title(t("window_title"))
root.geometry("340x460")
root.resizable(False, False)

lang_button = ttk.Button(root, text=t("btn_language"), command=toggle_language)
lang_button.pack(anchor="ne", padx=10, pady=(5, 0))

label_search = tk.Label(root, text=t("label_search"))
label_search.pack(pady=(5, 2))
job_entry = tk.Entry(root, width=35)
job_entry.pack(pady=(0, 5))

label_city = tk.Label(root, text=t("label_city"))
label_city.pack(pady=(5, 2))
city_entry = tk.Entry(root, width=35)
city_entry.pack(pady=(0, 5))

label_title = tk.Label(root, text=t("label_title"))
label_title.pack(pady=(5, 2))
title_entry = tk.Entry(root, width=35)
title_entry.pack(pady=(0, 5))

label_pages = tk.Label(root, text=t("label_pages"))
label_pages.pack(pady=(5, 2))
pages_entry = tk.Entry(root, width=10)
pages_entry.insert(0, "3")
pages_entry.pack(pady=(0, 5))

hiring_var = tk.BooleanVar()
hiring_check = tk.Checkbutton(
    root, text=t("checkbox_hiring"), variable=hiring_var
)
hiring_check.pack(pady=(5, 5))

start_button = ttk.Button(root, text=t("btn_start"), command=start_bot)
start_button.pack(pady=(10, 10))

root.mainloop()