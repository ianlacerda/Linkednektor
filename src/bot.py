import time
import random
import urllib.parse
import os
from playwright.sync_api import sync_playwright
from src.i18n import t, get_language
from src.db import init_db, is_profile_contacted, add_contacted_profile


active_pause_event = None
NOTES_BLOCKED_BY_PREMIUM = False


def check_pause(pause_event=None):
    """Blocks execution if active_pause_event is cleared."""
    global active_pause_event
    if pause_event is not None:
        active_pause_event = pause_event
    if active_pause_event and not active_pause_event.is_set():
        print(f"  ⏸️ {t('paused')}")
        active_pause_event.wait()
        print(f"  ▶️ {t('resumed')}")


def save_html_debug(page, profile_name):
    """Saves HTML source and a screenshot of the page to D:\\Documents\\linktest\\Linkednektor\\debug_dumps\\ for troubleshooting."""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        debug_dir = os.path.join(base_dir, "debug_dumps")
        os.makedirs(debug_dir, exist_ok=True)
        
        clean_name = "".join([c for c in profile_name if c.isalnum() or c in (" ", "_", "-")]).strip().replace(" ", "_")
        timestamp = int(time.time())
        
        # Save HTML
        html_filepath = os.path.join(debug_dir, f"{clean_name}_{timestamp}.html")
        html_content = page.content()
        with open(html_filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        # Save Screenshot
        screenshot_filepath = os.path.join(debug_dir, f"{clean_name}_{timestamp}.png")
        page.screenshot(path=screenshot_filepath)
        
        # Print with clickable file:/// links (convert Windows backslashes to forward slashes)
        link_html = f"file:///{html_filepath.replace('\\\\', '/').replace('\\', '/')}"
        link_png = f"file:///{screenshot_filepath.replace('\\\\', '/').replace('\\', '/')}"
        print(f"  📸 [DEBUG] Dump saved. HTML: {link_html} | Screenshot: {link_png}")
    except Exception as e:
        print(f"  ⚠️ [DEBUG] Failed to save debug files: {e}")


def save_search_results_debug(page, page_num):
    """Saves HTML source and a screenshot of the search results page to D:\\Documents\\linktest\\Linkednektor\\debug_dumps\\ for troubleshooting."""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        debug_dir = os.path.join(base_dir, "debug_dumps")
        os.makedirs(debug_dir, exist_ok=True)
        timestamp = int(time.time())
        
        # Save HTML
        html_filepath = os.path.join(debug_dir, f"search_results_page_{page_num}_{timestamp}.html")
        html_content = page.content()
        with open(html_filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        # Save Screenshot
        screenshot_filepath = os.path.join(debug_dir, f"search_results_page_{page_num}_{timestamp}.png")
        page.screenshot(path=screenshot_filepath)
        
        # Print with clickable file:/// links (convert Windows backslashes to forward slashes)
        link_html = f"file:///{html_filepath.replace('\\\\', '/').replace('\\', '/')}"
        link_png = f"file:///{screenshot_filepath.replace('\\\\', '/').replace('\\', '/')}"
        print(f"  📸 [DEBUG] Search results page {page_num} saved. HTML: {link_html} | Screenshot: {link_png}")
    except Exception as e:
        print(f"  ⚠️ [DEBUG] Failed to save search debug files: {e}")


# ===== AUTOMATION FUNCTIONS =====

def human_delay(min_time=2.0, max_time=4.0):
    seconds = random.uniform(min_time, max_time)
    steps = int(seconds / 0.2)
    for _ in range(steps):
        check_pause()
        time.sleep(0.2)
    rem = seconds - (steps * 0.2)
    if rem > 0:
        time.sleep(rem)


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
        const seen = new Set();
        
        let cards = document.querySelectorAll('.reusable-search__result-container');
        if (cards.length === 0) {
            cards = document.querySelectorAll('.entity-result');
        }
        if (cards.length === 0) {
            cards = document.querySelectorAll('ul.reusable-search__entity-result-list > li, ul[class*="results"] > li, .search-results-container li, li[class*="result"]');
        }
        if (cards.length === 0) {
            // Find all listitems or divs with role listitem, and filter out any nested ones
            const allItems = document.querySelectorAll('main div[role="listitem"], main li, div[role="listitem"], li');
            cards = Array.from(allItems).filter(item => {
                const parent = item.parentElement.closest('div[role="listitem"], li');
                return !parent && item.querySelector('a[href*="/in/"]');
            });
        }
        if (cards.length === 0) {
            cards = [document.body];
        }
        
        for (const card of cards) {
            const allLinks = card.querySelectorAll('a[href*="/in/"]');
            for (const link of allLinks) {
                // Skip mutual connections or badge insights
                if (link.closest('.entity-result__insights') || 
                    link.closest('.entity-result__simple-insight') ||
                    link.closest('.entity-result__badge') ||
                    link.closest('.entity-result__insights-v2')) {
                    continue;
                }
                
                const href = link.href;
                if (href && href.includes('/in/')) {
                    const cleanUrl = href.split('?')[0];
                    if (cleanUrl.match(/linkedin\\.com\\/in\\/[\\w-]+/) && !seen.has(cleanUrl)) {
                        seen.add(cleanUrl);
                        let name = link.textContent.trim().split('\\n')[0].trim();
                        if (!name || name.length < 2) {
                            const span = link.querySelector('span[aria-hidden="true"]');
                            if (span) name = span.textContent.trim();
                        }
                        results.push({
                            url: cleanUrl,
                            name: name || 'Unknown'
                        });
                        
                        // If we are processing per-card, only take the first link
                        if (card !== document.body) {
                            break;
                        }
                    }
                }
            }
        }
        return results;
    }""")

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
    """
    # Wait for the action buttons container to render (SPA loading protection)
    try:
        page.wait_for_selector(".pvs-profile-actions, .pv-top-card-v2-ctas, a[href*='contact-info']", timeout=8000)
    except:
        pass

    human_delay(2, 3)

    already_indicators = [
        "Pendente", "Pending",
    ]

    for indicator in already_indicators:
        loc = page.locator(f"button:has-text('{indicator}'), a:has-text('{indicator}')")
        if loc.count() > 0:
            try:
                if loc.first.is_visible():
                    print(f"  {t('already_connected')}")
                    return "already"
            except:
                pass

    connect_terms = [t("li_connect"), t("li_connect_alt"), "Connect", "Conectar"]
    seen_terms = set()
    unique_connect = []
    for ct in connect_terms:
        if ct not in seen_terms:
            seen_terms.add(ct)
            unique_connect.append(ct)

    for term in unique_connect:
        header_containers = [
            "[componentkey*='Topcard']",
            "[componentkey*='topcard']",
            ".pv-top-card",
            ".pvs-profile-actions",
            ".pv-top-card-v2-ctas",
        ]
        selectors = []
        for container in header_containers:
            selectors.extend([
                f"{container} a[href*='custom-invite']:has-text('{term}')",
                f"{container} a[href*='connect']:has-text('{term}')",
                f"{container} button:has-text('{term}')",
                f"{container} a:has-text('{term}')",
                f"{container} a[aria-label*='{term}']",
                f"{container} button[aria-label*='{term}']",
            ])
        for sel in selectors:
            loc = page.locator(sel)
            for i in range(loc.count()):
                try:
                    el = loc.nth(i)
                    if el.is_visible(timeout=2000):
                        try:
                            el.click(timeout=5000)
                            print(f"  {t('connect_visible')}")
                            return "found"
                        except:
                            tag = el.evaluate("el => el.tagName.toLowerCase()")
                            if tag == "span":
                                parent_btn = el.locator("xpath=..")
                                if parent_btn.count() > 0:
                                    parent_btn.first.click(timeout=5000)
                                    print(f"  {t('connect_visible')}")
                                    return "found"
                            raise
                except:
                    continue

    more_terms = ["More", "Mais"]
    more_btn = None
    header_containers = [
        "[componentkey*='Topcard']",
        "[componentkey*='topcard']",
        ".pv-top-card",
        ".pvs-profile-actions",
        ".pv-top-card-v2-ctas",
    ]
    for mterm in more_terms:
        selectors = []
        for container in header_containers:
            selectors.extend([
                f"{container} button[aria-label*='{mterm}']",
                f"{container} button:has-text('{mterm}')",
                f"{container} a:has-text('{mterm}')",
                f"{container} a[aria-label*='{mterm}']",
            ])
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

            # Check if there are "already connected / remove connection" indicators in the dropdown!
            remove_terms = [
                t("li_remove_connection"), t("li_remove_connection_alt"),
                "Remove Connection", "Remove connection", "Remover conexão", "Desfazer conexão",
                "Disconnect", "Desconectar", "Remover Conexão"
            ]
            seen_rterms = set()
            unique_rterms = []
            for rt in remove_terms:
                if rt not in seen_rterms:
                    seen_rterms.add(rt)
                    unique_rterms.append(rt)

            for rterm in unique_rterms:
                selectors_remove = [
                    f"div.artdeco-dropdown__content >> text={rterm}",
                    f"div[role='menu'] >> text={rterm}",
                    f"ul[role='menu'] >> text={rterm}",
                    f".artdeco-dropdown__content-inner >> text={rterm}",
                    f"div.pvs-overflow-actions-dropdown__content >> text={rterm}",
                ]
                for rsel in selectors_remove:
                    loc_remove = page.locator(rsel)
                    for ri in range(loc_remove.count()):
                        try:
                            if loc_remove.nth(ri).is_visible():
                                print(f"  {t('already_connected')} (detected '{rterm}' in More menu)")
                                page.keyboard.press("Escape")
                                return "already"
                        except:
                            pass

            for term in unique_connect:
                dropdown_selectors = [
                    f"div.artdeco-dropdown__content >> text={term}",
                    f"div.pvs-overflow-actions-dropdown__content >> text={term}",
                    f"div[role='menu'] >> text={term}",
                    f"ul[role='menu'] >> text={term}",
                    f"div[role='listbox'] >> text={term}",
                    f"div.artdeco-dropdown__content span:text-is('{term}')",
                    f"div.pvs-overflow-actions-dropdown__content span:text-is('{term}')",
                    f"div[role='menu'] span:text-is('{term}')",
                ]
                for sel in dropdown_selectors:
                    loc = page.locator(sel)
                    for i in range(loc.count()):
                        try:
                            el = loc.nth(i)
                            if el.is_visible(timeout=2000):
                                try:
                                    el.click(timeout=5000)
                                    print(f"  {t('connect_in_more')}")
                                    return "found"
                                except:
                                    parent_item = el.locator("xpath=ancestor::div[contains(@class,'artdeco-dropdown__item') or @role='menuitem' or contains(@class,'dropdown')]")
                                    if parent_item.count() > 0:
                                        parent_item.first.click(timeout=5000)
                                        print(f"  {t('connect_in_more')}")
                                        return "found"
                                    else:
                                        raise
                        except:
                            continue
        except Exception as e:
            print(f"  ⚠️ More menu error: {str(e)[:50]}")

        try:
            page.keyboard.press("Escape")
            time.sleep(0.5)
        except:
            pass

    print(f"  {t('connect_not_found')}")
    return "not_found"


def handle_connection_dialog(page, note_text=""):
    """Handles the connection invitation dialog with note limit warning and Premium fallback."""
    human_delay(1.5, 3)

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
        return True

    # Helper function to check and handle premium modal
    def check_and_handle_premium():
        premium_indicators = ["Premium", "Upgrade", "limite", "limit", "assinar", "subscribe", "personalizada", "personalized"]
        is_premium_visible = False
        for ind in premium_indicators:
            loc = page.locator(f"div.artdeco-modal:has-text('{ind}')")
            try:
                if loc.count() > 0 and loc.first.is_visible(timeout=1000):
                    is_premium_visible = True
                    break
            except:
                pass
        
        if is_premium_visible:
            print("    ⚠️ Premium limitation modal detected! Closing all modals and retrying connection request without note...")
            global NOTES_BLOCKED_BY_PREMIUM
            NOTES_BLOCKED_BY_PREMIUM = True
            
            # Dismiss premium modal by clicking close button first (X icon)
            close_clicked = False
            close_selectors = [
                "button[aria-label*='Close']",
                "button[aria-label*='close']",
                "button[aria-label*='Fechar']",
                "button[aria-label*='fechar']",
                "button[aria-label*='Dismiss']",
                "button[aria-label*='dismiss']",
                "button.artdeco-modal__dismiss",
                "[data-test-modal] button[aria-label*='Dismiss']",
                "[data-test-modal] button.artdeco-modal__dismiss",
            ]
            for sel in close_selectors:
                try:
                    loc = page.locator(sel)
                    if loc.count() > 0 and loc.first.is_visible(timeout=1000):
                        loc.first.click(timeout=2000)
                        close_clicked = True
                        break
                except:
                    pass
            
            if not close_clicked:
                page.keyboard.press("Escape")
            time.sleep(1.0)
            
            # Clean up all other overlays
            dismiss_overlays(page)
            time.sleep(1.0)
            return True
        return False

    success = False
    
    if note_text:
        # Enforce 300 character safety margin
        if len(note_text) > 300:
            print(f"  ⚠️ Note text exceeds 300 character limit ({len(note_text)}). Truncating to 300.")
            note_text = note_text[:300]

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

        # Check if clicking "Add a note" triggered a premium upgrade modal
        if check_and_handle_premium():
            print("    🔄 Retrying connection without note...")
            res = find_connect_button_on_profile(page)
            if res == "found":
                return handle_connection_dialog(page, note_text="")
            return False

        if note_clicked:
            human_delay(1, 2)

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
                try:
                    textarea.click(timeout=3000)
                    human_delay(0.3, 0.5)
                    textarea.fill("")
                    human_delay(0.3, 0.5)

                    for char in note_text:
                        textarea.type(char, delay=random.randint(30, 80))

                    print(f"    {t('note_added')}")
                    human_delay(1, 2)
                    
                    # Try to click Send
                    send_labels = [
                        t("li_send_now"), "Send now", "Enviar agora",
                        t("li_send"), "Send", "Enviar"
                    ]
                    sent_clicked = False
                    for label in send_labels:
                        loc = page.locator(f"button:has-text('{label}')")
                        if loc.count() > 0:
                            try:
                                loc.first.click(timeout=5000)
                                sent_clicked = True
                                break
                            except:
                                pass
                    
                    if sent_clicked:
                        # Wait a bit and check if a premium modal popped up after clicking send
                        time.sleep(1.5)
                        if check_and_handle_premium():
                            print("    🔄 Retrying connection without note...")
                            res = find_connect_button_on_profile(page)
                            if res == "found":
                                return handle_connection_dialog(page, note_text="")
                            return False
                        else:
                            success = True
                except Exception as ex:
                    print(f"    ⚠️ Note typing or sending failed: {ex}")
            else:
                print(f"    {t('note_failed')}")

    # Fallback / Direct Send (without note or if note sending was blocked)
    if not success:
        print(f"    {t('sent_direct')}")
        send_labels = [
            t("li_send_no_note"),
            "Send without a note", "Enviar sem nota",
            t("li_send_now"),
            "Send now", "Enviar agora",
            t("li_send"), "Send", "Enviar"
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

        # Ultimate fallback buttons
        for label in ["Send", "Enviar"]:
            loc3 = page.locator(f"button:has-text('{label}')")
            if loc3.count() > 0:
                try:
                    loc3.first.click(timeout=5000)
                    return True
                except:
                    pass

    return success


def process_page_via_profiles(page, max_left, note_text="", search_url=None, pause_event=None):
    """
    New approach: collects profile links, visits each one,
    finds Connect button (visible or in More menu), sends invitation with optional note.
    Registers contacted profiles in SQLite DB to avoid duplicate contacts.
    """
    profiles = collect_profile_links(page)

    if not profiles:
        print(f"  {t('no_buttons_left')}")
        return 0

    count_sent = 0
    consecutive_failures = 0
    max_failures_limit = 5

    for idx, profile in enumerate(profiles):
        # Check pause state
        check_pause(pause_event)

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

        # Skip profile if already contacted in database
        if is_profile_contacted(profile_url):
            print(f"  {t('skipping_contacted', name=profile_name)}")
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
                    # Save to DB
                    add_contacted_profile(profile_url, profile_name, "sent")
                else:
                    print(f"  {t('unexpected_state')}")
                    save_html_debug(page, profile_name)
                    dismiss_overlays(page)
                    consecutive_failures += 1

                human_delay(2, 4)

            elif result == "already":
                consecutive_failures = 0
                # Save to DB to avoid visiting again
                add_contacted_profile(profile_url, profile_name, "already_connected")

            else:
                consecutive_failures += 1
                save_html_debug(page, profile_name)

        except Exception as e:
            print(f"  {t('profile_error', msg=str(e)[:60])}")
            consecutive_failures += 1
            save_html_debug(page, profile_name)
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


def run_bot(city, job, title, num_pages, hiring, note_text="", on_complete=None, pause_event=None):
    global NOTES_BLOCKED_BY_PREMIUM
    NOTES_BLOCKED_BY_PREMIUM = False
    init_db()
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
                locale="en-US" if get_language() == "en" else "pt-BR",
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
                check_pause(pause_event)
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
                save_search_results_debug(page, page_num)

                max_left = max_per_run - total_sent
                if max_left <= 0:
                    print(f"\n{t('limit_reached', max=max_per_run)}")
                    break

                current_search_url = page.url

                sent = process_page_via_profiles(
                    page, max_left,
                    note_text=note_text,
                    search_url=current_search_url,
                    pause_event=pause_event
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
    finally:
        if on_complete:
            try:
                on_complete()
            except:
                pass
