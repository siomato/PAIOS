import re
from app.tools.browser_automation import browser_automation
from app.tools.target_resolver import target_resolver
from app.tools.browser_worker import browser_worker


class BrowserTools:

    # =========================================================
    # INTERNAL BROWSER STATE
    # =========================================================

    def _browser_state_worker(self):
        """
        Runs INSIDE BrowserWorker.

        IMPORTANT:
        Playwright Page/Browser/Context objects never leave
        the worker thread.
        """

        try:
            page = browser_automation.start()

            if page is None:
                return {
                    "current_url": None,
                    "page_title": None,
                    "error": None
                }

            try:
                current_url = page.url
            except Exception:
                current_url = None

            try:
                page_title = page.title()
            except Exception:
                page_title = None

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
    # GET BROWSER STATE
    # =========================================================

    def _get_browser_state(self):

        try:

            result = browser_worker.execute(
                self._browser_state_worker
            )

            if not isinstance(
                result,
                dict
            ):
                return {
                    "current_url": None,
                    "page_title": None
                }

            return {
                "current_url": result.get(
                    "current_url"
                ),
                "page_title": result.get(
                    "page_title"
                )
            }

        except Exception as e:

            print(
                f"⚠️ Browser telemetry failed: {e}"
            )

            return {
                "current_url": None,
                "page_title": None
            }

    # =========================================================
    # NORMALIZE RESULT
    # =========================================================

    def _with_telemetry(
        self,
        result
    ):
        """
        Add browser telemetry without allowing a Playwright
        object to escape the worker.
        """

        # -----------------------------------------------------
        # Result already contains telemetry
        # -----------------------------------------------------

        if isinstance(
            result,
            dict
        ):

            result = dict(
                result
            )

            # Some BrowserAutomation operations return:
            #
            # {
            #     "title": ...,
            #     "url": ...,
            #     "content": ...
            # }
            #
            # Normalize those fields.

            if (
                "current_url"
                not in result
            ):

                result[
                    "current_url"
                ] = result.get(
                    "url"
                )

            if (
                "page_title"
                not in result
            ):

                result[
                    "page_title"
                ] = result.get(
                    "title"
                )

            # -------------------------------------------------
            # Only request telemetry if necessary
            # -------------------------------------------------

            if (
                not result.get(
                    "current_url"
                )
                and
                not result.get(
                    "page_title"
                )
            ):

                telemetry = (
                    self._get_browser_state()
                )

                result[
                    "current_url"
                ] = telemetry.get(
                    "current_url"
                )

                result[
                    "page_title"
                ] = telemetry.get(
                    "page_title"
                )

            result[
                "browser_telemetry"
            ] = {
                "current_url":
                    result.get(
                        "current_url"
                    ),

                "page_title":
                    result.get(
                        "page_title"
                    )
            }

            return result

        # -----------------------------------------------------
        # String result
        # -----------------------------------------------------

        telemetry = (
            self._get_browser_state()
        )

        return {
            "status": "success",

            "message": str(
                result
            ),

            "data": None,

            "current_url":
                telemetry.get(
                    "current_url"
                ),

            "page_title":
                telemetry.get(
                    "page_title"
                ),

            "browser_telemetry":
                telemetry,

            "error": None
        }

    # =========================================================
    # OPEN URL
    # =========================================================

    def open_url(
        self,
        url: str
    ):

        if not url:

            raise ValueError(
                "URL cannot be empty."
            )

        print(
            "\n========== OPEN URL =========="
        )

        print(
            f"URL: {url}"
        )

        result = browser_worker.execute(
            browser_automation.open_url,
            url
        )

        if isinstance(
            result,
            str
        ):

            lowered = result.lower()

            if (
                "browser error"
                in lowered
                or
                "failed"
                in lowered
                or
                "error:"
                in lowered
            ):

                raise RuntimeError(
                    result
                )

        return self._with_telemetry(
            result
        )

    # =========================================================
    # SEARCH
    # =========================================================

    def search(
        self,
        query: str
    ):

        if not query:

            raise ValueError(
                "Search query cannot be empty."
            )

        query = query.strip()

        if not query:

            raise ValueError(
                "Search query cannot be empty."
            )

        print(
            "\n========== SEARCH =========="
        )

        print(
            f"Query: {query}"
        )

        result = browser_worker.execute(
            browser_automation.search,
            query
        )

        if isinstance(
            result,
            str
        ):

            lowered = result.lower()

            if (
                "search failed"
                in lowered
                or
                "browser error"
                in lowered
                or
                "error:"
                in lowered
            ):

                raise RuntimeError(
                    result
                )

        normalized = (
            self._with_telemetry(
                result
            )
        )

        print(
            "\n🔎 SEARCH TELEMETRY"
        )

        print(
            f"URL   : "
            f"{normalized.get('current_url')}"
        )

        print(
            f"TITLE : "
            f"{normalized.get('page_title')}"
        )

        return normalized

    # =========================================================
    # CLICK BUTTON — EXECUTED INSIDE WORKER
    # =========================================================

    def _click_button_worker(
        self,
        text
    ):
        """
        Entire Playwright button interaction happens inside
        BrowserWorker.
        """

        try:

            page = browser_automation.start()

            buttons = page.locator(
                "button"
            ).all()

            for button in buttons:

                try:

                    button_text = (
                        button
                        .inner_text()
                        .strip()
                    )

                    if (
                        button_text.lower()
                        ==
                        text.lower()
                    ):

                        button.click()

                        try:

                            page.wait_for_load_state(
                                "domcontentloaded",
                                timeout=10000
                            )

                        except Exception:
                            pass

                        try:
                            current_url = (
                                page.url
                            )
                        except Exception:
                            current_url = None

                        try:
                            page_title = (
                                page.title()
                            )
                        except Exception:
                            page_title = None

                        return {
                            "status": "success",

                            "message":
                                f"Clicked target: {text}",

                            "target": text,

                            "current_url":
                                current_url,

                            "page_title":
                                page_title,

                            "error": None
                        }

                except Exception:
                    continue

            return {
                "status": "failed",

                "message":
                    f"Button not found: {text}",

                "target": text,

                "current_url": None,

                "page_title": None,

                "error":
                    f"Button not found: {text}"
            }

        except Exception as e:

            return {
                "status": "failed",

                "message":
                    f"Button click failed: {e}",

                "target": text,

                "current_url": None,

                "page_title": None,

                "error": str(e)
            }


    # =========================================================
    # TARGET RESOLUTION — EXECUTED INSIDE BROWSER WORKER
    # =========================================================

    def _resolve_target_worker(self, target: str):
        """
        Resolve the target while running in BrowserWorker.

        This is required because TargetResolver may inspect
        Playwright state. No Playwright object is returned.
        """
        try:
            resolved = target_resolver.resolve(target)

            if not isinstance(resolved, dict):
                return None

            return dict(resolved)

        except Exception as e:
            print(f"⚠️ Target resolver failed: {e}")
            return {
                "_resolver_error": str(e)
            }

    # =========================================================
    # LIVE DOM CLICK FALLBACK — EXECUTED INSIDE WORKER
    # =========================================================

    def _click_dom_target_worker(self, target: str):
        """
        Find and click a natural-language target directly from
        the live DOM. All Playwright operations remain in the
        BrowserWorker thread.
        """

        target = " ".join(str(target).split()).strip()

        if not target:
            return {
                "status": "failed",
                "error": "Click target cannot be empty."
            }

        # Ignore terminal punctuation and normalize
        # natural-language click targets.
        normalized_target = str(
            target
        ).casefold().strip()

        normalized_target = re.sub(
            r"[.!?]+$",
            "",
            normalized_target
        ).strip()

        # ---------------------------------------------------------
        # Remove common click-action prefixes
        # ---------------------------------------------------------

        click_prefixes = (
            "click on ",
            "click the ",
            "click ",
            "press ",
            "select ",
            "choose ",
            "tap ",
            "on ",
        )

        for prefix in click_prefixes:

            if normalized_target.startswith(prefix):

                normalized_target = (
                    normalized_target[len(prefix):].strip()
                )
                break

        # Remove articles
        for prefix in ("the ", "a ", "an "):

            if normalized_target.startswith(prefix):

                normalized_target = (
                    normalized_target[len(prefix):].strip()
                )
                break

        # Remove semantic element suffixes
        # "downloads link" -> "downloads"
        for suffix in (
            " link",
            " button",
            " tab",
            " menu",
            " option",
            " item",
        ):

            if normalized_target.endswith(suffix):

                normalized_target = (
                    normalized_target[:-len(suffix)].strip()
                )
                break

        print(
            f"🎯 Normalized click target: {normalized_target}"
        )

        try:
            page = browser_automation.start()

            # -----------------------------------------------------
            # FAST SEMANTIC DOM RESOLUTION
            # -----------------------------------------------------
            # Prefer Playwright's semantic locators before scanning
            # the entire DOM. The legacy exhaustive scan remains
            # below as the final fallback.

            print(
                f"🎯 Fast DOM resolution: {normalized_target}"
            )

            fast_locators = [
                page.get_by_role(
                    "link",
                    name=normalized_target,
                    exact=True
                ),
                page.get_by_role(
                    "button",
                    name=normalized_target,
                    exact=True
                ),
                page.get_by_text(
                    normalized_target,
                    exact=True
                ),
                page.locator(
                    f'[aria-label="{normalized_target}"]'
                ),
                page.locator(
                    f'[title="{normalized_target}"]'
                ),
            ]

            for locator in fast_locators:

                try:
                    if locator.count() == 0:
                        continue

                    element = locator.first

                    element.wait_for(
                        state="visible",
                        timeout=2000
                    )

                    print(
                        "🎯 Fast DOM target found."
                    )

                    element.scroll_into_view_if_needed()

                    try:
                        element.click(
                            timeout=5000
                        )
                    except Exception as click_error:
                        print(
                            "⚠️ Normal fast click failed; "
                            f"retrying force=True: {click_error}"
                        )
                        element.click(
                            force=True,
                            timeout=5000
                        )

                    try:
                        page.wait_for_load_state(
                            "domcontentloaded",
                            timeout=5000
                        )
                    except Exception:
                        pass

                    try:
                        page.wait_for_timeout(300)
                    except Exception:
                        pass

                    return {
                        "status": "success",
                        "message": (
                            f"Clicked target: {target}"
                        ),
                        "target": target,
                        "current_url": page.url,
                        "page_title": page.title(),
                        "error": None
                    }

                except Exception as e:
                    print(
                        f"⚠️ Fast locator failed: {e}"
                    )
                    continue

            print(
                "🔄 Fast DOM resolution did not match; "
                "using structured/legacy resolution."
            )

            # -----------------------------------------------------
            # SEARCH-RESULT SEMANTIC TARGETS
            #
            # "first search result" is not literal DOM text.
            # It refers to the structured search result captured
            # by BrowserAutomation during the preceding search.
            # -----------------------------------------------------

            first_result_aliases = {
                "first result",
                "the first result",
                "first search result",
                "the first search result",
                "first search results",
                "the first search results",
                "first useful result",
                "the first useful result",
                "first useful results",
                "the first useful results",
            }

            if normalized_target in first_result_aliases:

                print(
                    "🎯 Resolving first search result "
                    "from structured search state..."
                )

                first_result = (
                    browser_automation
                    .get_first_search_result()
                )

                if first_result:

                    print(
                        "🔗 First search result:"
                    )
                    print(
                        f"   {first_result.get('text', '')}"
                    )
                    print(
                        f"   {first_result.get('href', '')}"
                    )

                    result = (
                        browser_automation
                        .click_target(
                            first_result
                        )
                    )

                    if (
                        isinstance(result, str)
                        and
                        (
                            "failed"
                            in result.casefold()
                            or
                            "error:"
                            in result.casefold()
                            or
                            "browser error"
                            in result.casefold()
                        )
                    ):

                        return {
                            "status": "failed",
                            "error": result
                        }

                    try:
                        page.wait_for_load_state(
                            "domcontentloaded",
                            timeout=10000
                        )
                    except Exception:
                        pass

                    try:
                        current_url = page.url
                    except Exception:
                        current_url = None

                    try:
                        page_title = page.title()
                    except Exception:
                        page_title = None

                    return {
                        "status": "success",
                        "message": (
                            "Clicked first search result."
                        ),
                        "target": (
                            first_result.get(
                                "text",
                                "first search result"
                            )
                        ),
                        "current_url": current_url,
                        "page_title": page_title,
                        "error": None
                    }

                # -------------------------------------------------
                # Structured result state unavailable:
                # inspect known search-result selectors directly.
                # -------------------------------------------------

                print(
                    "⚠️ Structured search state is empty."
                )

                search_result_selectors = [
                    "a.result__a",
                    "a[data-testid='result-title-a']",
                    ".result a.result__a",
                    "a:has(h3)",
                ]

                for result_selector in (
                    search_result_selectors
                ):

                    try:

                        result_link = (
                            page.locator(
                                result_selector
                            ).first
                        )

                        result_link.wait_for(
                            state="visible",
                            timeout=3000
                        )

                        result_text = " ".join(
                            result_link.inner_text().split()
                        ).strip()

                        result_link.scroll_into_view_if_needed()
                        result_link.click()

                        try:
                            page.wait_for_load_state(
                                "domcontentloaded",
                                timeout=10000
                            )
                        except Exception:
                            pass

                        try:
                            current_url = page.url
                        except Exception:
                            current_url = None

                        try:
                            page_title = page.title()
                        except Exception:
                            page_title = None

                        return {
                            "status": "success",
                            "message": (
                                "Clicked first live "
                                "search result."
                            ),
                            "target": (
                                result_text
                                or
                                "first search result"
                            ),
                            "current_url": current_url,
                            "page_title": page_title,
                            "error": None
                        }

                    except Exception:
                        continue

            # -----------------------------------------------------
            # DOMAIN-BASED SEARCH RESULT TARGET
            #
            # Supports:
            #     "the official Python.org result"
            # -----------------------------------------------------

            if (
                "python.org" in normalized_target
                and
                "result" in normalized_target
            ):

                print(
                    "🎯 Resolving Python.org search result..."
                )

                search_results = (
                    browser_automation
                    .get_search_results()
                )

                selected_result = None

                for search_result in (
                    search_results
                ):

                    href = str(
                        search_result.get(
                            "href",
                            ""
                        )
                    ).casefold()

                    result_text = str(
                        search_result.get(
                            "text",
                            ""
                        )
                    ).casefold()

                    if (
                        "python.org" in href
                        or
                        "python.org" in result_text
                    ):

                        selected_result = (
                            search_result
                        )
                        break

                if selected_result:

                    print(
                        "🔗 Python.org result found:"
                    )
                    print(
                        f"   {selected_result.get('text', '')}"
                    )
                    print(
                        f"   {selected_result.get('href', '')}"
                    )

                    result = (
                        browser_automation
                        .click_target(
                            selected_result
                        )
                    )

                    if (
                        isinstance(result, str)
                        and
                        (
                            "failed"
                            in result.casefold()
                            or
                            "error:"
                            in result.casefold()
                            or
                            "browser error"
                            in result.casefold()
                        )
                    ):

                        return {
                            "status": "failed",
                            "error": result
                        }

                    try:
                        page.wait_for_load_state(
                            "domcontentloaded",
                            timeout=10000
                        )
                    except Exception:
                        pass

                    try:
                        current_url = page.url
                    except Exception:
                        current_url = None

                    try:
                        page_title = page.title()
                    except Exception:
                        page_title = None

                    return {
                        "status": "success",
                        "message": (
                            "Clicked Python.org "
                            "search result."
                        ),
                        "target": (
                            selected_result.get(
                                "text",
                                "Python.org"
                            )
                        ),
                        "current_url": current_url,
                        "page_title": page_title,
                        "error": None
                    }

            # -----------------------------------------------------
            # SEMANTIC NAVIGATION TARGET
            #
            # Targets such as "Downloads" are normally navigation
            # links, not buttons. Resolve them from the live DOM
            # using visible text, aria-label, title and href.
            #
            # This is deliberately done BEFORE the generic fallback
            # so navigation links are handled deterministically.
            # -----------------------------------------------------

            semantic_target = " ".join(
                target.split()
            ).strip()

            navigation_aliases = {
    "downloads": {
        "downloads",
        "download",
    },

    "documentation": {
        "documentation",
        "docs",
        "documentation page",
        "docs page",
    },

    "about": {
        "about",
        "about us",
    },

    "success stories": {
        "success stories",
        "success story",
    },

    "community": {
        "community",
    },

    "jobs": {
        "jobs",
        "careers",
        "career",
    },
}

            target_variants = navigation_aliases.get(
                normalized_target,
                {normalized_target},
            )

            semantic_selectors = [
                "a[href]",
                "button",
                "[role='link']",
                "[role='button']",
                "nav a",
            ]

            for selector in semantic_selectors:

                try:
                    elements = page.locator(
                        selector
                    ).all()
                except Exception:
                    continue

                for element in elements:

                    try:
                        if not element.is_visible():
                            continue

                        text_value = " ".join(
                            element.inner_text().split()
                        ).strip().casefold()

                        aria_value = (
                            element.get_attribute(
                                "aria-label"
                            )
                            or ""
                        ).strip().casefold()

                        title_value = (
                            element.get_attribute(
                                "title"
                            )
                            or ""
                        ).strip().casefold()

                        href_value = (
                            element.get_attribute(
                                "href"
                            )
                            or ""
                        ).strip().casefold()

                        candidates = {
                            text_value,
                            aria_value,
                            title_value,
                        }

                        candidates.discard("")

                        # Exact semantic match.
                        matched = any(
                            candidate in target_variants
                            for candidate in candidates
                        )

                        # For a normal navigation target, also allow
                        # the target to identify the final href segment.
                        if (
                            not matched
                            and href_value
                        ):

                            # Normalize the href
                            href_path = (
                                href_value
                                .split("?")[0]
                                .split("#")[0]
                                .rstrip("/")
                            )

                            href_last_part = (
                                href_path
                                .split("/")[-1]
                                .casefold()
                            )

                            # Generic semantic href matching
                            href_aliases = {

                                "downloads": {
                                    "downloads",
                                    "download",
                                },

                                "documentation": {
                                    "documentation",
                                    "docs",
                                    "doc",
                                },

                                "about": {
                                    "about",
                                    "about-us",
                                },

                                "jobs": {
                                    "jobs",
                                    "careers",
                                    "career",
                                },

                                "community": {
                                    "community",
                                },

                            }

                            href_targets = href_aliases.get(
                                normalized_target,
                                set()
                            )

                            if (
                                href_last_part
                                in href_targets
                            ):
                                matched = True

                        if not matched:
                            continue

                        print(
                            "🎯 Semantic navigation target found:"
                        )
                        print(
                            f"   text={text_value}"
                        )
                        print(
                            f"   aria-label={aria_value}"
                        )
                        print(
                            f"   href={href_value}"
                        )

                        element.scroll_into_view_if_needed()

                        # Prefer the real DOM click here. Unlike
                        # page.goto(), this preserves browser behavior
                        # such as JS handlers and SPA navigation.
                        try:
                            element.click()
                        except Exception as click_error:
                            print(
                                "⚠️ Semantic DOM click failed; "
                                f"retrying with force=True: {click_error}"
                            )
                            element.click(force=True)

                        try:
                            page.wait_for_load_state(
                                "domcontentloaded",
                                timeout=10000
                            )
                        except Exception:
                            pass

                        try:
                            page.wait_for_timeout(
                                500
                            )
                        except Exception:
                            pass

                        try:
                            current_url = page.url
                        except Exception:
                            current_url = None

                        try:
                            page_title = page.title()
                        except Exception:
                            page_title = None

                        return {
                            "status": "success",
                            "message": (
                                f"Clicked target: "
                                f"{semantic_target}"
                            ),
                            "target": semantic_target,
                            "current_url": current_url,
                            "page_title": page_title,
                            "error": None,
                        }

                    except Exception:
                        continue

            selectors = [
                "a",
                "button",
                "[role='button']",
                "input[type='button']",
                "input[type='submit']",
            ]

            for selector in selectors:
                try:
                    elements = page.locator(selector).all()
                except Exception:
                    continue

                for element in elements:
                    try:
                        if not element.is_visible():
                            continue

                        element_text = " ".join(
                            element.inner_text().split()
                        ).strip()

                        if (
                            element_text
                            and
                            element_text.casefold()
                            == normalized_target
                        ):
                            print(
                                f"🎯 Exact DOM target found: "
                                f"{element_text}"
                            )

                            element.scroll_into_view_if_needed()

                            try:
                                element.click()
                            except Exception as click_error:
                                print(
                                    "⚠️ Normal DOM click failed; "
                                    f"retrying with force=True: {click_error}"
                                )
                                element.click(force=True)

                            try:
                                page.wait_for_load_state(
                                    "domcontentloaded",
                                    timeout=10000
                                )
                            except Exception:
                                pass

                            try:
                                current_url = page.url
                            except Exception:
                                current_url = None

                            try:
                                page_title = page.title()
                            except Exception:
                                page_title = None

                            return {
                                "status": "success",
                                "message": (
                                    f"Clicked target: "
                                    f"{element_text}"
                                ),
                                "target": element_text,
                                "current_url": current_url,
                                "page_title": page_title,
                                "error": None
                            }

                    except Exception:
                        continue

            for selector in selectors:
                try:
                    elements = page.locator(selector).all()
                except Exception:
                    continue

                for element in elements:
                    try:
                        if not element.is_visible():
                            continue

                        element_text = " ".join(
                            element.inner_text().split()
                        ).strip()

                        if (
                            element_text
                            and
                            normalized_target
                            in element_text.casefold()
                        ):
                            print(
                                f"🎯 Partial DOM target found: "
                                f"{element_text}"
                            )

                            element.scroll_into_view_if_needed()
                            element.click()

                            try:
                                page.wait_for_load_state(
                                    "domcontentloaded",
                                    timeout=10000
                                )
                            except Exception:
                                pass

                            try:
                                current_url = page.url
                            except Exception:
                                current_url = None

                            try:
                                page_title = page.title()
                            except Exception:
                                page_title = None

                            return {
                                "status": "success",
                                "message": (
                                    f"Clicked target: "
                                    f"{element_text}"
                                ),
                                "target": element_text,
                                "current_url": current_url,
                                "page_title": page_title,
                                "error": None
                            }

                    except Exception:
                        continue

            for attribute in (
                "aria-label",
                "title",
                "value",
            ):
                try:
                    elements = page.locator(
                        f"[{attribute}]"
                    ).all()
                except Exception:
                    continue

                for element in elements:
                    try:
                        if not element.is_visible():
                            continue

                        value = element.get_attribute(attribute)

                        if (
                            value
                            and
                            value.strip().casefold()
                            == normalized_target
                        ):
                            print(
                                f"🎯 Attribute target found: "
                                f"{value}"
                            )

                            element.scroll_into_view_if_needed()
                            element.click()

                            try:
                                page.wait_for_load_state(
                                    "domcontentloaded",
                                    timeout=10000
                                )
                            except Exception:
                                pass

                            try:
                                current_url = page.url
                            except Exception:
                                current_url = None

                            try:
                                page_title = page.title()
                            except Exception:
                                page_title = None

                            return {
                                "status": "success",
                                "message": (
                                    f"Clicked target: {value}"
                                ),
                                "target": value,
                                "current_url": current_url,
                                "page_title": page_title,
                                "error": None
                            }

                    except Exception:
                        continue

            return {
                "status": "failed",
                "error": (
                    f"Could not resolve target: {target}"
                )
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }

    # =========================================================
    # CLICK
    # =========================================================

    def click(
        self,
        target: str
    ):

        print(
            "\n========== CLICK TARGET =========="
        )

        print(
            f"Target: {target}"
        )

        if not target:
            raise ValueError(
                "Click target cannot be empty."
            )

        # =====================================================
        # PRIMARY PATH — LIVE DOM CLICK
        #
        # For ordinary natural-language targets such as
        # "Python Variables", the browser itself is the source
        # of truth. Click the actual DOM element first.
        #
        # This avoids converting a real click into page.goto(),
        # which can bypass JavaScript navigation/SPA behavior.
        #
        # Search-result aliases are handled by the structured
        # resolver below.
        # =====================================================

        normalized_target = " ".join(
            str(target).split()
        ).casefold()

        search_aliases = {
            "first result",
            "the first result",
            "first search result",
            "the first search result",
            "last result",
            "the last result",
            "last search result",
            "the last search result",
        }

        if normalized_target not in search_aliases:

            print(
                "🖱️ Primary strategy: live DOM click."
            )

            dom_result = browser_worker.execute(
                self._click_dom_target_worker,
                target
            )

            if (
                isinstance(dom_result, dict)
                and
                dom_result.get("status") == "success"
            ):

                print(
                    "✅ Live DOM click succeeded."
                )

                return dom_result

            # IMPORTANT:
            # A live DOM miss is a TARGET-RESOLUTION failure, not
            # a browser-session failure. Do not reset or destroy the
            # current browser session here. The existing TargetResolver
            # path below must get a chance to resolve the same target
            # while the current page is still alive.
            error = (
                dom_result.get(
                    "error",
                    f"Could not resolve target: {target}"
                )
                if isinstance(dom_result, dict)
                else
                f"Could not resolve target: {target}"
            )

            print(
                f"⚠️ Live DOM target resolution failed: {error}"
            )

            print(
                "🧠 Falling back to TargetResolver without resetting browser..."
            )

            # IMPORTANT:
            # Do NOT raise here. The SECONDARY PATH immediately below
            # is the intended semantic-resolution fallback.

        # =====================================================
        # SECONDARY PATH — TARGET RESOLVER
        # =====================================================

        resolved = browser_worker.execute(
            self._resolve_target_worker,
            target
        )

        if (
            isinstance(resolved, dict)
            and resolved.get("_resolver_error")
        ):
            print(
                "⚠️ Target resolver could not inspect "
                "the browser from its worker context."
            )
            resolved = None

        print(
            f"Resolved target: {resolved}"
        )

        # -----------------------------------------------------
        # Semantic resolver failed -> live DOM fallback.
        # Both run inside BrowserWorker.
        # -----------------------------------------------------

        if not resolved:
            print(
                "⚠️ Semantic resolver could not "
                "resolve target."
            )

            print(
                "🔄 Switching to live DOM "
                "target resolution..."
            )

            fallback = browser_worker.execute(
                self._click_dom_target_worker,
                target
            )

            if (
                isinstance(fallback, dict)
                and fallback.get("status") == "success"
            ):
                return fallback

            error = (
                fallback.get(
                    "error",
                    f"Could not resolve target: {target}"
                )
                if isinstance(fallback, dict)
                else f"Could not resolve target: {target}"
            )

            raise RuntimeError(error)

        target_type = resolved.get("type")

        # =====================================================
        # LINK
        # =====================================================

        if target_type == "link":

            href = resolved.get("href")
            text = resolved.get("text", "")

            if not href:
                raise RuntimeError(
                    "Resolved link has no href."
                )

            print(f"🔗 Link text: {text}")
            print(f"🌐 Link href: {href}")

            result = browser_worker.execute(
                browser_automation.open_url,
                href
            )

            if isinstance(result, str):
                lowered = result.lower()

                if (
                    "browser error" in lowered
                    or "failed" in lowered
                    or "error:" in lowered
                ):
                    raise RuntimeError(result)

            normalized = self._with_telemetry(result)

            normalized["message"] = (
                f"Clicked target: {text}"
            )
            normalized["target"] = text
            normalized["href"] = href

            return normalized

        # =====================================================
        # BUTTON
        # =====================================================

        if target_type == "button":

            text = resolved.get("text", "")

            print(f"🔘 Button: {text}")

            result = browser_worker.execute(
                self._click_button_worker,
                text
            )

            if (
                isinstance(result, dict)
                and result.get("status") == "failed"
            ):
                raise RuntimeError(
                    result.get(
                        "error",
                        "Button click failed."
                    )
                )

            return result

        # =====================================================
        # INPUT
        # =====================================================

        if target_type == "input":
            raise RuntimeError(
                "Input targets cannot be clicked "
                "through the current click pipeline."
            )

        # =====================================================
        # UNKNOWN TARGET TYPE
        # =====================================================

        print(
            "⚠️ Unsupported target type."
        )

        fallback = browser_worker.execute(
            self._click_dom_target_worker,
            target
        )

        if (
            isinstance(fallback, dict)
            and fallback.get("status") == "success"
        ):
            return fallback

        error = (
            fallback.get(
                "error",
                f"Unsupported target type: {target_type}"
            )
            if isinstance(fallback, dict)
            else f"Unsupported target type: {target_type}"
        )

        raise RuntimeError(error)

    # =========================================================
    # FILL
    # =========================================================

    def fill_from_command(
        self,
        target: str,
        text: str
    ):

        if not target:

            raise ValueError(
                "Fill target cannot be empty."
            )

        if text is None:

            raise ValueError(
                "Fill text cannot be None."
            )

        target = str(target).strip()
        text = str(text)

        if not target:

            raise ValueError(
                "Fill target cannot be empty."
            )

        print(
            "\n========== FILL TARGET =========="
        )

        print(
            f"Target: {target}"
        )

        print(
            f"Text: {text}"
        )

        result = browser_worker.execute(
            browser_automation.fill_from_command,
            target,
            text
        )

        if isinstance(
            result,
            str
        ):

            lowered = result.lower()

            if (
                "fill failed"
                in lowered
                or
                "browser error"
                in lowered
                or
                "error:"
                in lowered
            ):

                raise RuntimeError(
                    result
                )

        return self._with_telemetry(
            result
        )

    # =========================================================
    # PRESS KEY
    # =========================================================

    def press_key(
        self,
        key: str
    ):

        if not key:

            raise ValueError(
                "Key cannot be empty."
            )

        result = browser_worker.execute(
            browser_automation.press_key,
            key
        )

        if isinstance(
            result,
            str
        ):

            lowered = result.lower()

            if (
                "press failed"
                in lowered
                or
                "browser error"
                in lowered
                or
                "error:"
                in lowered
            ):

                raise RuntimeError(
                    result
                )

        return self._with_telemetry(
            result
        )

    # =========================================================
    # FIND TARGET
    # =========================================================

    def find(
        self,
        target: str
    ):
        """
        Resolve a target without interacting with it.

        FIND inspects the current browser state, resolves the
        requested target, and returns plain metadata. It never
        clicks or navigates.
        """

        print("\n========== FIND TARGET ==========")

        if not target:
            raise ValueError(
                "Find target cannot be empty."
            )

        target = " ".join(
            str(target).split()
        ).strip()

        if not target:
            raise ValueError(
                "Find target cannot be empty."
            )

        print(f"Target: {target}")

        # TargetResolver may inspect Playwright state, so it
        # must execute inside BrowserWorker.
        resolved = browser_worker.execute(
            self._resolve_target_worker,
            target
        )

        # Resolver execution failed.
        if (
            isinstance(resolved, dict)
            and resolved.get("_resolver_error")
        ):
            error = resolved.get("_resolver_error")

            print(
                f"⚠️ Target resolver failed: {error}"
            )

            return {
                "status": "failed",
                "message": f"Could not find target: {target}",
                "target": target,
                "found": False,
                "data": None,
                "error": error
            }

        # Target was not found.
        if not resolved:
            print(f"❌ Target not found: {target}")

            return {
                "status": "failed",
                "message": f"Could not find target: {target}",
                "target": target,
                "found": False,
                "data": None,
                "error": f"Target not found: {target}"
            }

        # FIND must never click. It only returns the resolved data.
        print(f"✅ Target found: {target}")
        print(f"🔎 Resolved target: {resolved}")

        result = {
            "status": "success",
            "message": f"Found target: {target}",
            "target": target,
            "found": True,
            "data": resolved,
            "error": None
        }

        return self._with_telemetry(result)

    # =========================================================
    # READ PAGE
    # =========================================================

    def read_page(self):

        print(
            "\n========== READ PAGE =========="
        )

        result = browser_worker.execute(
            browser_automation.read_page
        )

        if isinstance(
            result,
            dict
        ):

            if result.get(
                "error"
            ):

                raise RuntimeError(
                    result["error"]
                )

        return self._with_telemetry(
            result
        )

    # =========================================================
    # CURRENT URL
    # =========================================================

    def get_current_url(self):

        telemetry = (
            self._get_browser_state()
        )

        return telemetry.get(
            "current_url"
        )

    # =========================================================
    # CURRENT PAGE
    # =========================================================

    def get_page(self):
        """
        Never return a Playwright Page object.

        Return plain browser state instead.
        """

        return self._get_browser_state()

    # =========================================================
    # PAGE TITLE
    # =========================================================

    def get_page_title(self):

        telemetry = (
            self._get_browser_state()
        )

        return telemetry.get(
            "page_title"
        )

    # =========================================================
    # COMMON WEBSITES
    # =========================================================

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


# =============================================================
# GLOBAL INSTANCE
# =============================================================

browser_tools = BrowserTools()