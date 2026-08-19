from urllib.parse import quote_plus, urljoin

from playwright.sync_api import sync_playwright


print("🔥 BROWSER AUTOMATION MODULE LOADED 🔥")


class BrowserAutomation:

    # =========================================================
    # INIT
    # =========================================================

    def __init__(self):

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

        # -----------------------------------------------------
        # Search state
        # -----------------------------------------------------

        self.search_results = []

        self.last_search_query = ""

        self.last_search_engine = ""

    # =========================================================
    # SESSION CHECK
    # =========================================================

    def _session_alive(self):

        try:

            return (
                self.playwright is not None
                and self.browser is not None
                and self.browser.is_connected()
                and self.context is not None
                and self.page is not None
                and not self.page.is_closed()
            )

        except Exception:

            return False

    # =========================================================
    # PAGE CONTRACT CHECK
    # =========================================================

    def _is_valid_page(self, page):
        """
        Verify that the object is a real Playwright Page.

        BrowserAutomation.start() has one strict contract:
        it ALWAYS returns a Playwright Page object.
        """

        if page is None:
            return False

        if isinstance(page, dict):
            return False

        required_methods = (
            "goto",
            "locator",
            "title",
            "is_closed",
        )

        for method_name in required_methods:

            if not callable(
                getattr(
                    page,
                    method_name,
                    None
                )
            ):
                return False

        try:
            page.is_closed()
        except Exception:
            return False

        return True

    # =========================================================
    # START BROWSER
    # =========================================================

    def start(self):
        """
        Start or reuse the browser session.

        STRICT CONTRACT:
        This method ALWAYS returns a Playwright Page.
        It must never return a dictionary or application result.
        """

        # -----------------------------------------------------
        # Reuse existing browser
        # -----------------------------------------------------

        if self._session_alive():

            if self._is_valid_page(
                self.page
            ):
                return self.page

            print(
                "⚠️ Invalid browser page object detected."
            )

            self._cleanup()

        # -----------------------------------------------------
        # Remove stale session
        # -----------------------------------------------------

        self._cleanup()

        print(
            "🌐 Starting fresh Playwright session..."
        )

        # -----------------------------------------------------
        # Start Playwright
        # -----------------------------------------------------

        self.playwright = (
            sync_playwright().start()
        )

        # -----------------------------------------------------
        # Launch Chromium
        # -----------------------------------------------------

        self.browser = (
            self.playwright.chromium.launch(
                headless=False
            )
        )

        # -----------------------------------------------------
        # Create browser context
        # -----------------------------------------------------

        self.context = (
            self.browser.new_context(
                viewport={
                    "width": 1366,
                    "height": 768
                }
            )
        )

        # -----------------------------------------------------
        # Create page
        # -----------------------------------------------------

        self.page = (
            self.context.new_page()
        )

        # -----------------------------------------------------
        # STRICT CONTRACT CHECK
        # -----------------------------------------------------

        if not self._is_valid_page(
            self.page
        ):

            print(
                "❌ BrowserAutomation.start() created "
                "an invalid page object."
            )

            self._cleanup()

            raise RuntimeError(
                "BrowserAutomation.start() must return "
                "a Playwright Page."
            )

        print(
            "✅ Browser session ready."
        )

        print(
            "✅ BrowserAutomation.start() contract verified: "
            "Playwright Page."
        )

        return self.page

    # =========================================================
    # BROWSER STATE
    # =========================================================

    def get_browser_state(self):
        """
        Return browser telemetry as plain Python data.

        Playwright objects remain inside BrowserAutomation.
        Only normal Python values are returned.
        """

        try:

            page = self.start()

            current_url = None
            page_title = None

            try:
                current_url = page.url
            except Exception:
                pass

            try:
                page_title = page.title()
            except Exception:
                pass

            return {
                "current_url": current_url,
                "page_title": page_title,
                "error": None
            }

        except Exception as e:

            print(
                f"⚠️ Browser state failed: {e}"
            )

            return {
                "current_url": None,
                "page_title": None,
                "error": str(e)
            }

    # =========================================================
    # OPEN URL
    # =========================================================

    def open_url(self, url: str):

        if not url:

            return (
                "Browser error: URL cannot be empty."
            )

        try:

            page = self.start()

            print(
                f"🌐 Opening: {url}"
            )

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            print(
                f"✅ Opened: {page.url}"
            )

            return (
                f"Opened {page.url}"
            )

        except Exception as e:

            print(
                f"❌ Open URL failed: {e}"
            )

            return (
                f"Browser error: {e}"
            )

    # =========================================================
    # GOOGLE SEARCH
    # =========================================================

    def google_search(self, query: str):

        query = query.strip()

        if not query:

            self.search_results = []

            return (
                "Google search failed: "
                "empty query."
            )

        try:

            page = self.start()

            print(
                f"🔎 Searching Google for: {query}"
            )

            # -------------------------------------------------
            # Reset search state
            # -------------------------------------------------

            self.search_results = []

            self.last_search_query = query
            self.last_search_engine = "google"

            # -------------------------------------------------
            # Open Google
            # -------------------------------------------------

            encoded_query = quote_plus(query)

            google_url = (
                "https://www.google.com/search?q="
                + encoded_query
            )

            page.goto(
                google_url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            # -------------------------------------------------
            # Detect Google block
            # -------------------------------------------------

            if "/sorry/" in page.url:

                print(
                    "⚠️ Google blocked the automated "
                    "search request."
                )

                return (
                    "Google unavailable."
                )

            # -------------------------------------------------
            # Wait for Google result
            # -------------------------------------------------

            try:

                page.locator(
                    "a:has(h3)"
                ).first.wait_for(
                    state="visible",
                    timeout=10000
                )

            except Exception:

                print(
                    "⚠️ Google result links "
                    "were not detected."
                )

                return (
                    "Google unavailable."
                )

            # -------------------------------------------------
            # Extract results
            # -------------------------------------------------

            self.search_results = (
                self._extract_search_results(
                    engine="google"
                )
            )

            print(
                f"📋 Structured Google results: "
                f"{len(self.search_results)}"
            )

            if not self.search_results:

                print(
                    "⚠️ Google produced no "
                    "usable search results."
                )

                return (
                    "Google unavailable."
                )

            # -------------------------------------------------
            # Display results
            # -------------------------------------------------

            self._print_search_results()

            print(
                "✅ Google search results loaded."
            )

            return (
                f"Searching Google for "
                f"'{query}'. "
                f"Found {len(self.search_results)} results."
            )

        except Exception as e:

            self.search_results = []

            print(
                f"❌ Google search failed: {e}"
            )

            return (
                "Google unavailable."
            )

    # =========================================================
    # DUCKDUCKGO SEARCH
    # =========================================================

    def duckduckgo_search(self, query: str):

        query = query.strip()

        if not query:

            self.search_results = []

            return (
                "DuckDuckGo search failed: "
                "empty query."
            )

        try:

            page = self.start()

            print(
                f"🔎 Searching DuckDuckGo for: {query}"
            )

            # -------------------------------------------------
            # Reset state
            # -------------------------------------------------

            self.search_results = []

            self.last_search_query = query
            self.last_search_engine = "duckduckgo"

            # -------------------------------------------------
            # Use DDG HTML endpoint.
            #
            # This is generally easier to parse than the
            # dynamic DuckDuckGo frontend.
            # -------------------------------------------------

            encoded_query = quote_plus(query)

            url = (
                "https://html.duckduckgo.com/html/?q="
                + encoded_query
            )

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            # -------------------------------------------------
            # Wait for results
            # -------------------------------------------------

            selectors = [
                "a.result__a",
                "a[data-testid='result-title-a']",
                ".result a.result__a",
            ]

            result_count = 0

            for selector in selectors:

                try:

                    page.locator(
                        selector
                    ).first.wait_for(
                        state="visible",
                        timeout=5000
                    )

                    result_count = page.locator(
                        selector
                    ).count()

                    if result_count > 0:

                        break

                except Exception:

                    continue

            print(
                f"🌐 Current URL: {page.url}"
            )

            print(
                f"🔗 DuckDuckGo result links detected: "
                f"{result_count}"
            )

            # -------------------------------------------------
            # Extract
            # -------------------------------------------------

            if result_count > 0:

                self.search_results = (
                    self._extract_search_results(
                        engine="duckduckgo"
                    )
                )

            print(
                f"📋 Structured search results: "
                f"{len(self.search_results)}"
            )

            # -------------------------------------------------
            # Print
            # -------------------------------------------------

            if self.search_results:

                self._print_search_results()

                print(
                    "✅ DuckDuckGo search "
                    "results loaded."
                )

                return (
                    f"Searching DuckDuckGo for "
                    f"'{query}'. "
                    f"Found {len(self.search_results)} results."
                )

            print(
                "⚠️ DuckDuckGo result links "
                "were not detected."
            )

            return (
                "DuckDuckGo search completed "
                "but no usable results were found."
            )

        except Exception as e:

            self.search_results = []

            print(
                f"❌ DuckDuckGo search failed: {e}"
            )

            return (
                "DuckDuckGo unavailable."
            )

    # =========================================================
    # GENERIC SEARCH
    # =========================================================

    def search(self, query: str):

        query = query.strip()

        if not query:

            self.search_results = []

            return (
                "Search failed: empty query."
            )

        print(
            "\n========== SEARCH =========="
        )

        print(
            f"🔎 Generic search requested: {query}"
        )

        # -----------------------------------------------------
        # Clear old search results
        # -----------------------------------------------------

        self.search_results = []

        self.last_search_query = query
        self.last_search_engine = ""

        # -----------------------------------------------------
        # GOOGLE
        # -----------------------------------------------------

        print(
            "🌐 Trying Google..."
        )

        google_result = self.google_search(
            query
        )

        if self.search_results:

            print(
                f"✅ Google returned "
                f"{len(self.search_results)} results."
            )

            return google_result

        # -----------------------------------------------------
        # DUCKDUCKGO
        # -----------------------------------------------------

        print(
            "🔄 Google unavailable."
        )

        print(
            "🌐 Falling back to DuckDuckGo..."
        )

        duck_result = (
            self.duckduckgo_search(
                query
            )
        )

        if self.search_results:

            print(
                f"✅ DuckDuckGo returned "
                f"{len(self.search_results)} results."
            )

            return duck_result

        # -----------------------------------------------------
        # FAILURE
        # -----------------------------------------------------

        print(
            "❌ No search results found."
        )

        return (
            f"Search completed for "
            f"'{query}', but no results "
            f"could be extracted."
        )

    # =========================================================
    # EXTRACT SEARCH RESULTS
    # =========================================================

    def _extract_search_results(
        self,
        engine="auto"
    ):

        if not self._session_alive():

            return []

        page = self.page

        # -----------------------------------------------------
        # Selector priority
        # -----------------------------------------------------

        if engine == "google":

            selectors = [
                "a:has(h3)"
            ]

        elif engine == "duckduckgo":

            selectors = [
                "a.result__a",
                "a[data-testid='result-title-a']",
                ".result a.result__a",
            ]

        else:

            selectors = [
                "a:has(h3)",
                "a.result__a",
                "a[data-testid='result-title-a']",
                "a:has(h2)",
            ]

        results = []

        seen = set()

        # -----------------------------------------------------
        # Extract
        # -----------------------------------------------------

        for selector in selectors:

            try:

                links = page.locator(
                    selector
                ).all()

            except Exception:

                continue

            for link in links:

                try:

                    href = (
                        link.get_attribute(
                            "href"
                        )
                    )

                    if not href:

                        continue

                    href = href.strip()

                    if not href:

                        continue

                    # -------------------------------------------------
                    # Ignore fragments
                    # -------------------------------------------------

                    if href.startswith("#"):

                        continue

                    # -------------------------------------------------
                    # Ignore Google internal URLs
                    # -------------------------------------------------

                    if (
                        "google.com/search" in href
                        or "google.com/sorry" in href
                    ):

                        continue

                    # -------------------------------------------------
                    # Ignore DuckDuckGo internal URLs
                    # -------------------------------------------------

                    if (
                        "duckduckgo.com/?q=" in href
                    ):

                        continue

                    # -------------------------------------------------
                    # Convert relative URL
                    # -------------------------------------------------

                    href = urljoin(
                        page.url,
                        href
                    )

                    # -------------------------------------------------
                    # Text
                    # -------------------------------------------------

                    try:

                        text = (
                            link.inner_text()
                            .strip()
                        )

                    except Exception:

                        text = ""

                    text = " ".join(
                        text.split()
                    )

                    if not text:

                        continue

                    # -------------------------------------------------
                    # Deduplicate
                    # -------------------------------------------------

                    key = href.lower()

                    if key in seen:

                        continue

                    seen.add(key)

                    # -------------------------------------------------
                    # Build result
                    # -------------------------------------------------

                    result = {

                        "index":
                            len(results) + 1,

                        "type":
                            "link",

                        "text":
                            text[:500],

                        "title":
                            text[:500],

                        "href":
                            href,

                        "url":
                            href,
                    }

                    results.append(
                        result
                    )

                except Exception:

                    continue

        return results

    # =========================================================
    # PRINT SEARCH RESULTS
    # =========================================================

    def _print_search_results(self):

        print(
            "\n========== SEARCH RESULTS =========="
        )

        for result in self.search_results[:10]:

            print(
                f"{result['index']}. "
                f"{result['title']}"
            )

            print(
                f"   {result['href']}"
            )

        print(
            "===================================="
        )

    # =========================================================
    # GET SEARCH RESULTS
    # =========================================================

    def get_search_results(self):

        return list(
            self.search_results
        )

    # =========================================================
    # GET FIRST SEARCH RESULT
    # =========================================================

    def get_first_search_result(self):

        if not self.search_results:

            return None

        return self.search_results[0]

    # =========================================================
    # GET LAST SEARCH RESULT
    # =========================================================

    def get_last_search_result(self):

        if not self.search_results:

            return None

        return self.search_results[-1]

    # =========================================================
    # CLICK SELECTOR
    # =========================================================

    def click(self, selector: str):

        if not selector:

            return (
                "Click failed: "
                "selector cannot be empty."
            )

        try:

            page = self.start()

            element = page.locator(
                selector
            ).first

            element.wait_for(
                state="visible",
                timeout=10000
            )

            element.click()

            try:

                page.wait_for_load_state(
                    "domcontentloaded",
                    timeout=10000
                )

            except Exception:

                pass

            return (
                f"Clicked element: "
                f"{selector}"
            )

        except Exception as e:

            return (
                f"Click failed: {e}"
            )

    # =========================================================
    # CLICK RESOLVED TARGET
    # =========================================================

    def click_target(self, target):

        if not target:

            return (
                "Click failed: "
                "target is None."
            )

        try:

            page = self.start()

            href = (
                target.get("href")
                or target.get("url")
            )

            text = (
                target.get("text")
                or target.get("title")
                or ""
            ).strip()

            print(
                "\n========== CLICK TARGET =========="
            )

            print(
                f"🎯 Target text: {text}"
            )

            print(
                f"🔗 Target href: {href}"
            )

            before_url = page.url

            print(
                f"🌐 Before URL: {before_url}"
            )

            # =================================================
            # STRATEGY 1 — DIRECT URL
            # =================================================

            if href:

                print(
                    "🎯 Using resolved target URL..."
                )

                try:

                    page.goto(
                        href,
                        wait_until="domcontentloaded",
                        timeout=30000
                    )

                    after_url = page.url

                    print(
                        f"🌐 After URL: {after_url}"
                    )

                    print(
                        "✅ Navigation verified."
                    )

                    return (
                        f"Clicked target: "
                        f"{text}"
                    )

                except Exception as e:

                    print(
                        f"⚠️ Direct URL navigation "
                        f"failed: {e}"
                    )

            # =================================================
            # STRATEGY 2 — HREF MATCH
            # =================================================

            if href:

                try:

                    links = page.locator(
                        "a"
                    ).all()

                    for link in links:

                        try:

                            link_href = (
                                link.get_attribute(
                                    "href"
                                )
                            )

                            if not link_href:

                                continue

                            absolute_href = urljoin(
                                page.url,
                                link_href
                            )

                            if (
                                absolute_href
                                != href
                            ):

                                continue

                            print(
                                "🎯 Matching href found."
                            )

                            link.click()

                            try:

                                page.wait_for_load_state(
                                    "domcontentloaded",
                                    timeout=15000
                                )

                            except Exception:

                                pass

                            return (
                                f"Clicked target: "
                                f"{text}"
                            )

                        except Exception:

                            continue

                except Exception:

                    pass

            # =================================================
            # STRATEGY 3 — EXACT TEXT
            # =================================================

            if text:

                try:

                    links = page.locator(
                        "a"
                    ).all()

                    for link in links:

                        try:

                            link_text = (
                                link.inner_text()
                                .strip()
                            )

                            if (
                                link_text
                                == text
                            ):

                                print(
                                    "🎯 Exact text "
                                    "match found."
                                )

                                link.click()

                                try:

                                    page.wait_for_load_state(
                                        "domcontentloaded",
                                        timeout=15000
                                    )

                                except Exception:

                                    pass

                                return (
                                    f"Clicked target: "
                                    f"{text}"
                                )

                        except Exception:

                            continue

                except Exception:

                    pass

            # =================================================
            # STRATEGY 4 — PARTIAL TEXT
            # =================================================

            if text:

                try:

                    links = page.locator(
                        "a"
                    ).all()

                    for link in links:

                        try:

                            link_text = (
                                link.inner_text()
                                .strip()
                            )

                            if (
                                text.lower()
                                in link_text.lower()
                            ):

                                print(
                                    "🎯 Partial text "
                                    "match found."
                                )

                                link.click()

                                try:

                                    page.wait_for_load_state(
                                        "domcontentloaded",
                                        timeout=15000
                                    )

                                except Exception:

                                    pass

                                return (
                                    f"Clicked target: "
                                    f"{text}"
                                )

                        except Exception:

                            continue

                except Exception:

                    pass

            return (
                "Click failed: "
                "target element not found."
            )

        except Exception as e:

            print(
                f"❌ Click target failed: {e}"
            )

            return (
                f"Click target failed: {e}"
            )

    # =========================================================
    # FILL SELECTOR
    # =========================================================

    def fill(
        self,
        selector: str,
        text: str
    ):

        try:

            page = self.start()

            element = page.locator(
                selector
            ).first

            element.wait_for(
                state="visible",
                timeout=10000
            )

            element.fill(
                text
            )

            return (
                f"Filled element: "
                f"{selector}"
            )

        except Exception as e:

            return (
                f"Fill failed: {e}"
            )

    # =========================================================
    # PRESS SELECTOR
    # =========================================================

    def press(
        self,
        selector: str,
        key: str
    ):

        try:

            page = self.start()

            element = page.locator(
                selector
            ).first

            element.wait_for(
                state="visible",
                timeout=10000
            )

            element.press(
                key
            )

            return (
                f"Pressed {key} "
                f"on {selector}"
            )

        except Exception as e:

            return (
                f"Press failed: {e}"
            )

    # =========================================================
    # PRESS KEY ON CURRENT PAGE
    # =========================================================

    def press_key(self, key: str):

        if not key:

            return (
                "Press failed: "
                "key cannot be empty."
            )

        try:

            page = self.start()

            print(
                f"⌨️ Pressing key: {key}"
            )

            before_url = page.url

            page.keyboard.press(
                key
            )

            # -------------------------------------------------
            # Navigation synchronization for Enter
            # -------------------------------------------------

            if key.casefold() == "enter":

                print(
                    "⏳ Checking for navigation..."
                )

                try:

                    page.wait_for_function(
                        """
                        (beforeUrl) => {
                            return window.location.href !== beforeUrl;
                        }
                        """,
                        before_url,
                        timeout=10000
                    )

                    print(
                        "🌐 Navigation detected."
                    )

                except Exception:

                    print(
                        "ℹ️ No URL change detected."
                    )

                try:

                    page.wait_for_load_state(
                        "domcontentloaded",
                        timeout=10000
                    )

                except Exception:

                    print(
                        "ℹ️ DOMContentLoaded wait timed out."
                    )

                try:

                    page.wait_for_timeout(
                        300
                    )

                except Exception:
                    pass

                print(
                    f"🌐 Final URL: {page.url}"
                )

                try:

                    print(
                        f"📄 Final title: {page.title()}"
                    )

                except Exception:
                    pass

            return (
                f"Pressed {key}"
            )

        except Exception as e:

            return (
                f"Press failed: {e}"
            )


    # =========================================================
    # FILL FROM COMMAND
    # =========================================================

    def fill_from_command(
        self,
        target: str,
        text: str
    ):
        """
        Fill a browser input identified by a natural-language target.

        Example:
            target = "search box"
            text = "Python asyncio tutorial"
        """

        if not target or not target.strip():
            return "Fill failed: target is empty."

        if text is None:
            return "Fill failed: text is empty."

        target = " ".join(
            str(target).split()
        ).strip()

        text = str(text)

        try:

            page = self.start()

            if page is None:
                return (
                    "Fill failed: "
                    "browser page is not available."
                )

            normalized_target = (
                " ".join(
                    target.split()
                ).casefold()
            )

            print(
                "\n========== FILL TARGET =========="
            )
            print(f"Target: {target}")
            print(f"Text: {text}")
            print(
                f"Normalized target: {normalized_target}"
            )

            aliases = {
                "search box": {
                    "search",
                    "search box",
                    "search field",
                    "search input",
                    "search bar",
                },
                "email": {
                    "email",
                    "email field",
                    "email input",
                    "email address",
                },
                "username": {
                    "username",
                    "username field",
                    "username input",
                    "user name",
                },
                "password": {
                    "password",
                    "password field",
                    "password input",
                },
                "message": {
                    "message",
                    "message field",
                    "message box",
                    "message input",
                    "message area",
                    "text area",
                },
            }

            target_variants = aliases.get(
                normalized_target,
                {normalized_target}
            )

            selectors = [
                "input",
                "textarea",
                "[contenteditable='true']",
            ]

            for selector in selectors:

                try:
                    elements = page.locator(
                        selector
                    ).all()
                except Exception as selector_error:
                    print(
                        "⚠️ Could not inspect selector "
                        f"{selector}: {selector_error}"
                    )
                    continue

                for element in elements:

                    try:

                        if not element.is_visible():
                            continue

                        placeholder = (
                            element.get_attribute(
                                "placeholder"
                            ) or ""
                        ).strip().casefold()

                        name = (
                            element.get_attribute(
                                "name"
                            ) or ""
                        ).strip().casefold()

                        aria_label = (
                            element.get_attribute(
                                "aria-label"
                            ) or ""
                        ).strip().casefold()

                        title = (
                            element.get_attribute(
                                "title"
                            ) or ""
                        ).strip().casefold()

                        element_id = (
                            element.get_attribute(
                                "id"
                            ) or ""
                        ).strip().casefold()

                        input_type = (
                            element.get_attribute(
                                "type"
                            ) or ""
                        ).strip().casefold()

                        candidates = {
                            placeholder,
                            name,
                            aria_label,
                            title,
                            element_id,
                            input_type,
                        }

                        candidates.discard("")

                        print(
                            "🔎 Candidate:",
                            candidates
                        )

                        matched = False

                        for candidate in candidates:
                            if candidate in target_variants:
                                matched = True
                                break

                        if not matched:
                            for candidate in candidates:
                                for variant in target_variants:
                                    if (
                                        variant
                                        and (
                                            variant in candidate
                                            or candidate in variant
                                        )
                                    ):
                                        matched = True
                                        break
                                if matched:
                                    break

                        if not matched and normalized_target in {
                            "search",
                            "search box",
                            "search field",
                            "search input",
                            "search bar",
                        }:
                            if input_type == "search":
                                matched = True

                        if not matched and normalized_target in {
                            "email",
                            "email field",
                            "email input",
                            "email address",
                        }:
                            if input_type == "email":
                                matched = True

                        if not matched and normalized_target in {
                            "password",
                            "password field",
                            "password input",
                        }:
                            if input_type == "password":
                                matched = True

                        if not matched:
                            continue

                        print(
                            "\n🎯 FILL TARGET RESOLVED"
                        )
                        print(f"   Target      : {target}")
                        print(f"   Placeholder : {placeholder}")
                        print(f"   Name        : {name}")
                        print(f"   ARIA label  : {aria_label}")
                        print(f"   ID          : {element_id}")
                        print(f"   Type        : {input_type}")

                        element.scroll_into_view_if_needed()
                        element.fill(text)

                        print(
                            "✅ Input filled successfully."
                        )

                        return (
                            f"Filled {target} "
                            f"with '{text}'"
                        )

                    except Exception as element_error:

                        print(
                            "⚠️ Input candidate failed: "
                            f"{element_error}"
                        )
                        continue

            return (
                "Fill failed: "
                f"could not resolve '{target}'."
            )

        except Exception as e:

            return (
                f"Fill failed: {e}"
            )


    # =========================================================
    # READ PAGE
    # =========================================================

    def read_page(self):

        print(
            "\n📖 Reading current page..."
        )

        try:

            page = self.start()

            # -------------------------------------------------
            # Wait for DOM
            # -------------------------------------------------

            try:

                page.wait_for_load_state(
                    "domcontentloaded",
                    timeout=15000
                )

            except Exception as e:

                print(
                    f"⚠️ DOM wait skipped: {e}"
                )

            # -------------------------------------------------
            # Title
            # -------------------------------------------------

            try:

                title = page.title()

            except Exception:

                title = ""

            # -------------------------------------------------
            # URL
            # -------------------------------------------------

            try:

                url = page.url

            except Exception:

                url = ""

            # -------------------------------------------------
            # Body
            # -------------------------------------------------

            content = ""

            try:

                body = page.locator(
                    "body"
                )

                body.wait_for(
                    state="attached",
                    timeout=10000
                )

                content = (
                    body.inner_text(
                        timeout=15000
                    )
                )

            except Exception as e:

                print(
                    f"⚠️ Body extraction "
                    f"failed: {e}"
                )

            # -------------------------------------------------
            # Fallback to HTML
            # -------------------------------------------------

            if len(content.strip()) < 20:

                try:

                    content = (
                        page.locator(
                            "html"
                        ).inner_text(
                            timeout=10000
                        )
                    )

                except Exception:

                    pass

            # -------------------------------------------------
            # Output
            # -------------------------------------------------

            print(
                f"📄 Page title: {title}"
            )

            print(
                f"🌐 Page URL: {url}"
            )

            print(
                f"📄 Content length: "
                f"{len(content)}"
            )

            if len(content.strip()) < 20:

                print(
                    "⚠️ Page content is very small."
                )

            return {

                "title":
                    title,

                "url":
                    url,

                "content":
                    content[:10000]
            }

        except Exception as e:

            print(
                f"❌ Read page failed: {e}"
            )

            return {

                "title": "",

                "url": "",

                "content": "",

                "error":
                    str(e)
            }

    # =========================================================
    # CURRENT URL
    # =========================================================

    def get_current_url(self):

        if self._session_alive():

            try:

                return self.page.url

            except Exception:

                pass

        return (
            "No active browser session."
        )

    # =========================================================
    # CURRENT PAGE
    # =========================================================

    def get_page(self):

        if self._session_alive():

            return self.page

        return self.start()

    # =========================================================
    # OPEN YOUTUBE
    # =========================================================

    def open_youtube(self):

        return self.open_url(
            "https://www.youtube.com"
        )

    # =========================================================
    # OPEN CHATGPT
    # =========================================================

    def open_chatgpt(self):

        return self.open_url(
            "https://chatgpt.com"
        )

    # =========================================================
    # OPEN GITHUB
    # =========================================================

    def open_github(self):

        return self.open_url(
            "https://github.com"
        )

    # =========================================================
    # OPEN LINKEDIN
    # =========================================================

    def open_linkedin(self):

        return self.open_url(
            "https://www.linkedin.com"
        )

    # =========================================================
    # OPEN GMAIL
    # =========================================================

    def open_gmail(self):

        return self.open_url(
            "https://mail.google.com"
        )

    # =========================================================
    # CLEANUP
    # =========================================================

    def _cleanup(self):

        # -----------------------------------------------------
        # Page
        # -----------------------------------------------------

        try:

            if (
                self.page
                and not self.page.is_closed()
            ):

                self.page.close()

        except Exception:

            pass

        # -----------------------------------------------------
        # Context
        # -----------------------------------------------------

        try:

            if self.context:

                self.context.close()

        except Exception:

            pass

        # -----------------------------------------------------
        # Browser
        # -----------------------------------------------------

        try:

            if (
                self.browser
                and self.browser.is_connected()
            ):

                self.browser.close()

        except Exception:

            pass

        # -----------------------------------------------------
        # Playwright
        # -----------------------------------------------------

        try:

            if self.playwright:

                self.playwright.stop()

        except Exception:

            pass

        # -----------------------------------------------------
        # Reset state
        # -----------------------------------------------------

        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None

        self.search_results = []

    # =========================================================
    # CLOSE
    # =========================================================

    def close(self):

        print(
            "🔴 Closing browser..."
        )

        self._cleanup()

        print(
            "✅ Browser closed."
        )

        return (
            "Browser closed."
        )


# =============================================================
# GLOBAL INSTANCE
# =============================================================

browser_automation = BrowserAutomation()