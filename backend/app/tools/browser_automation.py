"""
PAIOS Browser Automation Engine

Features:
- Playwright browser control
- Global web search
- Context-aware website search
- YouTube search
- GitHub search
- Reddit search
- Stack Overflow search
- Amazon search
- Google/Bing/DuckDuckGo search
- URL navigation
- Click
- Fill / type
- Keyboard actions
- Hover
- Select
- Check / uncheck
- Scrolling
- Back / forward / reload
- Browser tabs
- Screenshots
- Page reading
- Element discovery
- Search-result extraction
- Site shortcuts
- Access-control integration
"""

from __future__ import annotations

import re
import time

from pathlib import Path
from urllib.parse import quote_plus, urlparse, urljoin

from app.tools.browser_worker import browser_worker
from app.security.access_control import access_controller

try:
    from playwright.sync_api import sync_playwright
except Exception:
    sync_playwright = None


class BrowserAutomation:

    # ================================================================
    # KNOWN WEBSITE SEARCH URLS
    # ================================================================

    SITE_SEARCH_URLS = {
        "youtube.com":
            "https://www.youtube.com/results?search_query={query}",

        "youtu.be":
            "https://www.youtube.com/results?search_query={query}",

        "github.com":
            "https://github.com/search?q={query}",

        "reddit.com":
            "https://www.reddit.com/search/?q={query}",

        "stackoverflow.com":
            "https://stackoverflow.com/search?q={query}",

        "stackexchange.com":
            "https://stackexchange.com/search?q={query}",

        "amazon.com":
            "https://www.amazon.com/s?k={query}",

        "amazon.in":
            "https://www.amazon.in/s?k={query}",

        "google.com":
            "https://www.google.com/search?q={query}",

        "bing.com":
            "https://www.bing.com/search?q={query}",

        "duckduckgo.com":
            "https://duckduckgo.com/?q={query}",

        "python.org":
            "https://www.python.org/search/?q={query}",

        "wikipedia.org":
            "https://www.wikipedia.org/w/index.php?search={query}",

        "npmjs.com":
            "https://www.npmjs.com/search?q={query}",
    }

    # ================================================================
    # CONSTRUCTOR
    # ================================================================

    def __init__(self):

        self.pw = None
        self.browser = None
        self.context = None
        self.page = None

        # Search state
        self.search_results = []
        self.last_search_query = ""
        self.last_search_engine = ""
        self.last_search_scope = ""

        # Browser state
        self.last_url = ""
        self.last_title = ""

    # ================================================================
    # BROWSER START
    # ================================================================

    def start(self):

        # Browser already running
        if self.page and not self.page.is_closed():
            return self.page

        if sync_playwright is None:
            raise RuntimeError(
                "Playwright is not installed. "
                "Run: pip install playwright"
            )

        # Start Playwright
        self.pw = sync_playwright().start()

        # Launch Chromium
        self.browser = self.pw.chromium.launch(
            headless=False
        )

        # Browser context
        self.context = self.browser.new_context(
            accept_downloads=True,
            viewport={
                "width": 1440,
                "height": 900,
            },
        )

        # First tab
        self.page = self.context.new_page()

        return self.page

    # ================================================================
    # TELEMETRY
    # ================================================================

    def _telemetry(self):

        page = self.start()

        try:
            title = page.title()
        except Exception:
            title = ""

        self.last_url = page.url
        self.last_title = title

        return {
            "current_url": page.url,
            "page_title": title,
        }

    # ================================================================
    # URL NORMALIZATION
    # ================================================================

    def _normalize_url(self, url):

        url = str(url).strip()

        if not url:
            raise ValueError(
                "URL cannot be empty"
            )

        # Already has protocol
        if re.match(
            r"^https?://",
            url,
            re.IGNORECASE,
        ):
            return url

        # Add HTTPS
        return "https://" + url

    # ================================================================
    # OPEN URL
    # ================================================================

    def open_url(self, url):

        url = self._normalize_url(url)

        access_controller.authorize_url(url)

        page = self.start()

        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=30000,
        )

        self.last_url = page.url

        try:
            self.last_title = page.title()
        except Exception:
            self.last_title = ""

        return {
            "status": "success",
            "action": "open_url",
            "url": page.url,
            "title": self.last_title,
        }

    # ================================================================
    # CURRENT DOMAIN
    # ================================================================

    def _current_domain(self):

        page = self.start()

        try:
            host = urlparse(
                page.url
            ).netloc.lower()
        except Exception:
            return ""

        if host.startswith("www."):
            host = host[4:]

        return host

    # ================================================================
    # CHECK WHETHER DOMAIN MATCHES
    # ================================================================

    def _domain_matches(self, host, domain):

        host = host.lower().strip()
        domain = domain.lower().strip()

        if host.startswith("www."):
            host = host[4:]

        if domain.startswith("www."):
            domain = domain[4:]

        return (
            host == domain
            or host.endswith("." + domain)
        )

    # ================================================================
    # HUMAN-VERIFICATION DETECTION
    # ================================================================

    def _is_verification_page(self, engine=None):
        """Return True when the current page looks like an anti-bot challenge."""
        page = self.start()
        try:
            title = page.title() or ""
        except Exception:
            title = ""
        try:
            body = page.locator("body").inner_text(timeout=5000) or ""
        except Exception:
            body = ""

        haystack = (title + "\n" + body).lower()
        markers = (
            "captcha",
            "recaptcha",
            "hcaptcha",
            "verify you are human",
            "verify that you are human",
            "are you human",
            "human verification",
            "robot check",
            "unusual traffic",
            "automated queries",
            "confirm you are not a robot",
            "not a robot",
            "security check",
            "checking your browser",
            "challenge-platform",
            "/sorry/",
        )
        return any(marker in haystack for marker in markers)

    # ================================================================
    # GLOBAL SEARCH
    # ================================================================

    def _global_search(
        self,
        query,
        engine="auto",
    ):

        page = self.start()

        query = str(query).strip()

        if not query:
            raise ValueError(
                "Search query cannot be empty"
            )

        if engine == "auto":

            # Automatic search intentionally avoids DuckDuckGo because
            # it may present human-verification challenges to automation.
            engines = [
                "google",
                "bing",
            ]

        else:

            engines = [
                str(engine).lower().strip()
            ]

        search_urls = {
            "google":
                "https://www.google.com/search?q=",

            "bing":
                "https://www.bing.com/search?q=",

            "duckduckgo":
                "https://duckduckgo.com/?q=",
        }

        last_error = None

        for current_engine in engines:

            if current_engine not in search_urls:
                continue

            try:

                base_url = search_urls[
                    current_engine
                ]

                target_url = (
                    base_url
                    + quote_plus(query)
                )

                access_controller.authorize_url(
                    target_url
                )

                page.goto(
                    target_url,
                    wait_until="domcontentloaded",
                    timeout=20000,
                )

                # Small wait for dynamic results
                try:
                    page.wait_for_timeout(700)
                except Exception:
                    pass

                if self._is_verification_page(current_engine):
                    raise RuntimeError(
                        f"{current_engine} presented a human-verification page."
                    )

                results = (
                    self._extract_global_results(current_engine)
                )

                if not results:
                    raise RuntimeError(
                        f"{current_engine} returned no usable external results."
                    )

                self.search_results = results
                self.last_search_query = query
                self.last_search_engine = (
                    current_engine
                )
                self.last_search_scope = "web"

                self.last_url = page.url

                try:
                    self.last_title = page.title()
                except Exception:
                    self.last_title = ""

                return {
                    "status": "success",
                    "action": "search",
                    "scope": "web",
                    "engine": current_engine,
                    "query": query,
                    "results": results,
                    "url": page.url,
                    "title": self.last_title,
                }

            except Exception as exc:

                last_error = exc

        raise RuntimeError(
            "No usable search engine. "
            f"Last error: {last_error}"
        )

    # ================================================================
    # SEARCH
    # ================================================================

    def search(
        self,
        query,
        engine="auto",
    ):
        """
        Intelligent search.

        Behavior:

        1. If a supported website is currently open:
           search inside that website.

        2. If the website has no direct search URL:
           try to find its search box.

        3. If no website search is possible:
           use Google, then Bing.
        """

        query = str(query).strip()

        if not query:
            raise ValueError(
                "Search query cannot be empty"
            )

        page = self.start()

        current_url = (
            page.url or ""
        ).lower()

        # ------------------------------------------------------------
        # If user explicitly requested a search engine,
        # always use that engine.
        # ------------------------------------------------------------

        if engine != "auto":

            return self._global_search(
                query,
                engine,
            )

        # ------------------------------------------------------------
        # Blank page -> global search
        # ------------------------------------------------------------

        if current_url in (
            "",
            "about:blank",
            "about:blank#",
        ):

            return self._global_search(
                query,
                "auto",
            )

        # ------------------------------------------------------------
        # Try current website
        # ------------------------------------------------------------

        site_result = (
            self._search_current_site(
                query
            )
        )

        if site_result is not None:
            return site_result

        # ------------------------------------------------------------
        # Current site could not be searched.
        # Fall back to global web search.
        # ------------------------------------------------------------

        return self._global_search(
            query,
            "auto",
        )

    # ================================================================
    # CURRENT WEBSITE SEARCH
    # ================================================================

    def _search_current_site(
        self,
        query,
    ):

        page = self.start()

        host = self._current_domain()

        if not host:
            return None

        # ------------------------------------------------------------
        # Known website direct-search URL
        # ------------------------------------------------------------

        for domain, template in (
            self.SITE_SEARCH_URLS.items()
        ):

            if not self._domain_matches(
                host,
                domain,
            ):
                continue

            try:

                target_url = template.format(
                    query=quote_plus(query)
                )

                access_controller.authorize_url(
                    target_url
                )

                page.goto(
                    target_url,
                    wait_until="domcontentloaded",
                    timeout=25000,
                )

                try:
                    page.wait_for_timeout(800)
                except Exception:
                    pass

                results = (
                    self._extract_site_results()
                )

                self.search_results = results
                self.last_search_query = query
                self.last_search_engine = domain
                self.last_search_scope = "site"

                self.last_url = page.url

                try:
                    self.last_title = page.title()
                except Exception:
                    self.last_title = ""

                return {
                    "status": "success",
                    "action": "search",
                    "scope": "site",
                    "site": domain,
                    "query": query,
                    "results": results,
                    "url": page.url,
                    "title": self.last_title,
                }

            except Exception:
                # Direct search failed.
                # Continue to search-box strategy.
                break

        # ------------------------------------------------------------
        # Generic website search-box strategy
        # ------------------------------------------------------------

        return self._search_using_page_input(
            query
        )

    # ================================================================
    # GENERIC WEBSITE SEARCH BOX
    # ================================================================

    def _search_using_page_input(
        self,
        query,
    ):

        page = self.start()

        selectors = [

            # HTML search inputs
            'input[type="search"]',

            # Common names
            'input[name="q"]',
            'input[name="query"]',
            'input[name="search"]',
            'input[name="keyword"]',

            # Placeholders
            'input[placeholder*="search" i]',
            'input[placeholder*="find" i]',

            # Accessibility
            'input[aria-label*="search" i]',
            'input[aria-label*="find" i]',

            # Textareas
            'textarea[placeholder*="search" i]',

            # ARIA searchbox
            '[role="searchbox"]',
        ]

        for selector in selectors:

            try:

                locator = page.locator(
                    selector
                )

                count = locator.count()

                if count <= 0:
                    continue

                for index in range(
                    min(count, 10)
                ):

                    target = locator.nth(
                        index
                    )

                    try:

                        if not target.is_visible():
                            continue

                        if not target.is_editable():
                            continue

                        target.fill(query)

                        target.press("Enter")

                        try:

                            page.wait_for_load_state(
                                "domcontentloaded",
                                timeout=10000,
                            )

                        except Exception:
                            pass

                        try:
                            page.wait_for_timeout(
                                500
                            )
                        except Exception:
                            pass

                        self.search_results = (
                            self._extract_site_results()
                        )

                        self.last_search_query = (
                            query
                        )

                        self.last_search_engine = (
                            self._current_domain()
                        )

                        self.last_search_scope = (
                            "site"
                        )

                        self.last_url = page.url

                        try:
                            self.last_title = (
                                page.title()
                            )
                        except Exception:
                            self.last_title = ""

                        return {
                            "status": "success",
                            "action": "search",
                            "scope": "site",
                            "site": self._current_domain(),
                            "query": query,
                            "results": self.search_results,
                            "url": page.url,
                            "title": self.last_title,
                            "method": "search_box",
                        }

                    except Exception:
                        continue

            except Exception:
                continue

        return None

    # ================================================================
    # GOOGLE SEARCH
    # ================================================================

    def google_search(self, query):

        return self._global_search(
            query,
            "google",
        )

    # ================================================================
    # BING SEARCH
    # ================================================================

    def bing_search(self, query):

        return self._global_search(
            query,
            "bing",
        )

    # ================================================================
    # DUCKDUCKGO SEARCH
    # ================================================================

    def duckduckgo_search(self, query):

        return self._global_search(
            query,
            "duckduckgo",
        )

    # ================================================================
    # GLOBAL SEARCH RESULT EXTRACTION
    # ================================================================

    def _extract_global_results(self, engine=None):
        """Extract real external results from Google or Bing.

        Search engines change their HTML frequently, so use engine-specific
        selectors first and a conservative generic fallback second.
        """
        page = self.start()
        engine = (engine or self.last_search_engine or "").lower().strip()
        results = []
        seen_urls = set()

        def add_result(text, href):
            try:
                text = re.sub(r"\s+", " ", str(text or "")).strip()
                href = str(href or "").strip()
                if not text or len(text) < 2 or not href:
                    return

                # Google redirect URLs.
                if href.startswith("/url?"):
                    match = re.search(r"[?&]q=([^&]+)", href)
                    if match:
                        from urllib.parse import unquote
                        href = unquote(match.group(1))

                if href.startswith("//"):
                    href = "https:" + href
                elif href.startswith("/"):
                    href = urljoin(page.url, href)

                if not re.match(r"^https?://", href, re.IGNORECASE):
                    return

                parsed = urlparse(href)
                host = parsed.netloc.lower().split(":", 1)[0]
                blocked = {
                    "google.com", "www.google.com", "google.co.in",
                    "www.google.co.in", "bing.com", "www.bing.com",
                    "duckduckgo.com", "www.duckduckgo.com",
                }
                if host in blocked or host.endswith(".google.com") or host.endswith(".bing.com"):
                    return

                # Ignore obvious search-engine/navigation endpoints.
                if href.lower().startswith((
                    "https://www.google.com/search",
                    "https://www.bing.com/search",
                    "https://duckduckgo.com/?q=",
                )):
                    return

                key = href.split("#", 1)[0]
                if key in seen_urls:
                    return
                seen_urls.add(key)
                results.append({
                    "title": text[:240],
                    "url": href,
                })
            except Exception:
                return

        # ------------------------------------------------------------
        # Google: result links normally contain an <h3>.
        # ------------------------------------------------------------
        if engine == "google":
            selectors = [
                "a:has(h3)",
                "div#search a[href]:has(h3)",
                "div.MjjYud a[href]:has(h3)",
            ]
            for selector in selectors:
                try:
                    anchors = page.locator(selector).all()
                    for anchor in anchors:
                        try:
                            h3 = anchor.locator("h3").first
                            title = h3.inner_text() if h3.count() else anchor.inner_text()
                            href = anchor.get_attribute("href") or ""
                            add_result(title, href)
                        except Exception:
                            continue
                        if len(results) >= 20:
                            return results
                    if results:
                        return results
                except Exception:
                    continue

        # ------------------------------------------------------------
        # Bing: result links are normally inside li.b_algo h2.
        # ------------------------------------------------------------
        if engine == "bing":
            selectors = [
                "li.b_algo h2 a[href]",
                "main li.b_algo h2 a[href]",
                "ol#b_results li.b_algo h2 a[href]",
            ]
            for selector in selectors:
                try:
                    anchors = page.locator(selector).all()
                    for anchor in anchors:
                        try:
                            add_result(
                                anchor.inner_text(),
                                anchor.get_attribute("href") or "",
                            )
                        except Exception:
                            continue
                        if len(results) >= 20:
                            return results
                    if results:
                        return results
                except Exception:
                    continue

        # ------------------------------------------------------------
        # Conservative generic fallback. This is deliberately used only
        # after engine-specific extraction so navigation links do not win.
        # ------------------------------------------------------------
        try:
            anchors = page.locator("a[href]").all()
        except Exception:
            anchors = []

        for anchor in anchors:
            try:
                text = anchor.inner_text() or ""
                href = anchor.get_attribute("href") or ""
                add_result(text, href)
                if len(results) >= 20:
                    break
            except Exception:
                continue

        return results

    # ================================================================
    # SITE SEARCH RESULT EXTRACTION
    # ================================================================

    def _extract_site_results(self):

        page = self.start()

        results = []
        seen = set()

        try:

            anchors = page.locator(
                "a[href]"
            ).all()

        except Exception:

            return results

        for anchor in anchors:

            try:

                href = (
                    anchor.get_attribute(
                        "href"
                    )
                    or ""
                )

                text = (
                    anchor.inner_text()
                    or ""
                ).strip()

                if not href:
                    continue

                if not text:
                    continue

                if len(text) < 2:
                    continue

                if href.startswith(
                    "javascript:"
                ):
                    continue

                if href.startswith(
                    "#"
                ):
                    continue

                # Relative links
                if href.startswith(
                    "/"
                ):

                    href = urljoin(
                        page.url,
                        href,
                    )

                if not re.match(
                    r"^https?://",
                    href,
                    re.IGNORECASE,
                ):
                    continue

                key = (
                    text,
                    href,
                )

                if key in seen:
                    continue

                seen.add(key)

                results.append(
                    {
                        "title": text[:240],
                        "url": href,
                    }
                )

                if len(results) >= 20:
                    break

            except Exception:
                continue

        return results

    # ================================================================
    # SEARCH RESULT ACCESS
    # ================================================================

    def get_search_results(self):

        return list(
            self.search_results
        )

    def get_first_search_result(self):

        if not self.search_results:
            return None

        return self.search_results[0]

    def get_last_search_result(self):

        if not self.search_results:
            return None

        return self.search_results[-1]

    # ================================================================
    # TARGET RESOLUTION
    # ================================================================

    def _resolve(self, target):

        page = self.start()

        target = str(
            target
        ).strip()

        if not target:
            raise ValueError(
                "Browser target cannot be empty"
            )

        pattern = re.compile(
            re.escape(target),
            re.IGNORECASE,
        )

        # ------------------------------------------------------------
        # Buttons
        # ------------------------------------------------------------

        try:

            locator = page.get_by_role(
                "button",
                name=pattern,
            )

            if locator.count() > 0:
                return locator

        except Exception:
            pass

        # ------------------------------------------------------------
        # Links
        # ------------------------------------------------------------

        try:

            locator = page.get_by_role(
                "link",
                name=pattern,
            )

            if locator.count() > 0:
                return locator

        except Exception:
            pass

        # ------------------------------------------------------------
        # Text
        # ------------------------------------------------------------

        try:

            locator = page.get_by_text(
                pattern
            )

            if locator.count() > 0:
                return locator

        except Exception:
            pass

        # ------------------------------------------------------------
        # Placeholder
        # ------------------------------------------------------------

        try:

            locator = page.locator(
                "input[placeholder]"
            )

            count = locator.count()

            for index in range(
                min(count, 20)
            ):

                item = locator.nth(
                    index
                )

                try:

                    placeholder = (
                        item.get_attribute(
                            "placeholder"
                        )
                        or ""
                    )

                    if re.search(
                        pattern,
                        placeholder,
                    ):

                        return item

                except Exception:
                    continue

        except Exception:
            pass

        # ------------------------------------------------------------
        # aria-label
        # ------------------------------------------------------------

        try:

            locator = page.locator(
                "[aria-label]"
            )

            count = locator.count()

            for index in range(
                min(count, 20)
            ):

                item = locator.nth(
                    index
                )

                try:

                    label = (
                        item.get_attribute(
                            "aria-label"
                        )
                        or ""
                    )

                    if re.search(
                        pattern,
                        label,
                    ):

                        return item

                except Exception:
                    continue

        except Exception:
            pass

        raise ValueError(
            f"Could not resolve browser target: "
            f"{target}"
        )

    # ================================================================
    # CLICK
    # ================================================================

    def click(self, target):

        page = self.start()

        target = str(
            target
        ).strip()

        # ------------------------------------------------------------
        # First search result
        # ------------------------------------------------------------

        if target.lower() in (
            "first search result",
            "first result",
            "the first result",
        ):

            result = (
                self.get_first_search_result()
            )

            if result:

                return self.open_url(
                    result["url"]
                )

            raise ValueError(
                "No search results available."
            )

        # ------------------------------------------------------------
        # Last search result
        # ------------------------------------------------------------

        if target.lower() in (
            "last search result",
            "last result",
            "the last result",
        ):

            result = (
                self.get_last_search_result()
            )

            if result:

                return self.open_url(
                    result["url"]
                )

            raise ValueError(
                "No search results available."
            )

        # ------------------------------------------------------------
        # Normal target
        # ------------------------------------------------------------

        locator = self._resolve(
            target
        )

        locator.first.click(
            timeout=15000
        )

        try:
            page.wait_for_timeout(300)
        except Exception:
            pass

        return {
            "status": "success",
            "action": "click",
            "target": target,
            "url": page.url,
            "title": page.title(),
        }

    # ================================================================
    # FILL
    # ================================================================

    def fill(
        self,
        target,
        text,
    ):

        page = self.start()

        target = str(
            target
        ).strip()

        text = str(
            text
        )

        locator = self._resolve(
            target
        )

        locator.first.fill(
            text
        )

        return {
            "status": "success",
            "action": "fill",
            "target": target,
            "text": text,
            "url": page.url,
        }

    # ================================================================
    # COMMAND COMPATIBILITY
    # ================================================================

    def fill_from_command(
        self,
        target,
        text,
    ):

        return self.fill(
            target,
            text,
        )

    # ================================================================
    # PRESS KEY
    # ================================================================

    def press_key(self, key):

        page = self.start()

        key = str(
            key
        ).strip()

        if not key:
            raise ValueError(
                "Key cannot be empty"
            )

        page.keyboard.press(
            key
        )

        return {
            "status": "success",
            "action": "press",
            "key": key,
            "url": page.url,
        }

    # ================================================================
    # PRESS ALIAS
    # ================================================================

    def press(self, key):

        return self.press_key(
            key
        )

    # ================================================================
    # HOVER
    # ================================================================

    def hover(self, target):

        target = str(
            target
        ).strip()

        locator = self._resolve(
            target
        )

        locator.first.hover(
            timeout=15000
        )

        return {
            "status": "success",
            "action": "hover",
            "target": target,
        }

    # ================================================================
    # SELECT DROPDOWN
    # ================================================================

    def select(
        self,
        target,
        value,
    ):

        target = str(
            target
        ).strip()

        value = str(
            value
        )

        locator = self._resolve(
            target
        )

        locator.first.select_option(
            label=value
        )

        return {
            "status": "success",
            "action": "select",
            "target": target,
            "value": value,
        }

    # ================================================================
    # CHECK
    # ================================================================

    def check(self, target):

        target = str(
            target
        ).strip()

        locator = self._resolve(
            target
        )

        locator.first.check()

        return {
            "status": "success",
            "action": "check",
            "target": target,
        }

    # ================================================================
    # UNCHECK
    # ================================================================

    def uncheck(self, target):

        target = str(
            target
        ).strip()

        locator = self._resolve(
            target
        )

        locator.first.uncheck()

        return {
            "status": "success",
            "action": "uncheck",
            "target": target,
        }

    # ================================================================
    # SCROLL
    # ================================================================

    def scroll(self, amount=700):

        page = self.start()

        amount = float(
            amount
        )

        page.mouse.wheel(
            0,
            amount
        )

        return {
            "status": "success",
            "action": "scroll",
            "amount": amount,
            "url": page.url,
        }

    # ================================================================
    # WAIT
    # ================================================================

    def wait(self, seconds=1):

        seconds = max(
            0,
            float(seconds)
        )

        time.sleep(
            seconds
        )

        return {
            "status": "success",
            "action": "wait",
            "seconds": seconds,
        }

    # ================================================================
    # BACK
    # ================================================================

    def back(self):

        page = self.start()

        try:

            page.go_back(
                wait_until="domcontentloaded",
                timeout=20000,
            )

        except Exception:
            # No previous history
            pass

        return self._telemetry()

    # ================================================================
    # FORWARD
    # ================================================================

    def forward(self):

        page = self.start()

        try:

            page.go_forward(
                wait_until="domcontentloaded",
                timeout=20000,
            )

        except Exception:
            pass

        return self._telemetry()

    # ================================================================
    # RELOAD
    # ================================================================

    def reload(self):

        page = self.start()

        page.reload(
            wait_until="domcontentloaded",
            timeout=20000,
        )

        return self._telemetry()

    # ================================================================
    # NEW TAB
    # ================================================================

    def new_tab(self, url=None):

        self.start()

        page = self.context.new_page()

        self.page = page

        if url:

            return self.open_url(
                url
            )

        return {
            "status": "success",
            "action": "new_tab",
            "url": page.url,
            "title": "",
        }

    # ================================================================
    # CLOSE TAB
    # ================================================================

    def close_tab(self):

        page = self.start()

        try:
            page.close()
        except Exception:
            pass

        pages = [
            item
            for item in self.context.pages
            if not item.is_closed()
        ]

        if pages:

            self.page = pages[-1]

        else:

            self.page = (
                self.context.new_page()
            )

        return self._telemetry()

    # ================================================================
    # LIST TABS
    # ================================================================

    def tabs(self):

        self.start()

        results = []

        for index, page in enumerate(
            self.context.pages
        ):

            try:

                title = (
                    page.title()
                    if not page.is_closed()
                    else ""
                )

            except Exception:

                title = ""

            results.append(
                {
                    "index": index,
                    "url": page.url,
                    "title": title,
                    "closed": page.is_closed(),
                }
            )

        return results

    # ================================================================
    # SWITCH TAB
    # ================================================================

    def switch_tab(self, index):

        self.start()

        index = int(
            index
        )

        pages = self.context.pages

        if index < 0:
            raise IndexError(
                "Tab index cannot be negative."
            )

        if index >= len(pages):
            raise IndexError(
                f"Tab {index} does not exist. "
                f"Available tabs: {len(pages)}"
            )

        self.page = pages[index]

        return self._telemetry()

    # ================================================================
    # SCREENSHOT
    # ================================================================

    def screenshot(
        self,
        path=None,
        full_page=True,
    ):

        page = self.start()

        destination = (
            path
            or str(
                Path.home()
                / "Downloads"
                / "paios_browser.png"
            )
        )

        access_controller.authorize(
            "filesystem_write",
            target=destination,
        )

        page.screenshot(
            path=destination,
            full_page=bool(
                full_page
            ),
        )

        return {
            "status": "success",
            "action": "screenshot",
            "path": destination,
            "url": page.url,
        }

    # ================================================================
    # READ PAGE
    # ================================================================

    def read_page(self):

        page = self.start()

        text = page.locator(
            "body"
        ).inner_text(
            timeout=15000
        )

        return {
            "status": "success",
            "action": "read",
            "url": page.url,
            "title": page.title(),
            "content": text[:30000],
        }

    # ================================================================
    # FIND ELEMENT
    # ================================================================

    def find(self, target):

        target = str(
            target
        ).strip()

        locator = self._resolve(
            target
        )

        return {
            "status": "success",
            "action": "find",
            "target": target,
            "count": locator.count(),
        }

    # ================================================================
    # CURRENT URL
    # ================================================================

    def get_current_url(self):

        return self.start().url

    # ================================================================
    # CURRENT PAGE
    # ================================================================

    def get_page(self):

        return self.start()

    # ================================================================
    # CURRENT TITLE
    # ================================================================

    def get_page_title(self):

        return self.start().title()

    # ================================================================
    # SITE SHORTCUTS
    # ================================================================

    def open_youtube(self):

        return self.open_url(
            "https://www.youtube.com"
        )

    def open_chatgpt(self):

        return self.open_url(
            "https://chatgpt.com"
        )

    def open_github(self):

        return self.open_url(
            "https://github.com"
        )

    def open_linkedin(self):

        return self.open_url(
            "https://www.linkedin.com"
        )

    def open_gmail(self):

        return self.open_url(
            "https://mail.google.com"
        )

    def open_reddit(self):

        return self.open_url(
            "https://www.reddit.com"
        )

    def open_stackoverflow(self):

        return self.open_url(
            "https://stackoverflow.com"
        )

    def open_amazon(self):

        return self.open_url(
            "https://www.amazon.in"
        )

    # ================================================================
    # CLOSE BROWSER
    # ================================================================

    def close(self):

        # Close current page
        try:

            if self.page:
                self.page.close()

        except Exception:
            pass

        # Close context
        try:

            if self.context:
                self.context.close()

        except Exception:
            pass

        # Close browser
        try:

            if self.browser:
                self.browser.close()

        except Exception:
            pass

        # Stop Playwright
        try:

            if self.pw:
                self.pw.stop()

        except Exception:
            pass

        self.page = None
        self.context = None
        self.browser = None
        self.pw = None

        self.search_results = []

        return {
            "status": "success",
            "message": "Browser closed",
        }


# ================================================================
# SINGLETON
# ================================================================

browser_automation = BrowserAutomation()