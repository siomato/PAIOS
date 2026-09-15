"""
PAIOS Action Planner
====================

Deterministic natural-language planner for browser + laptop automation.

The planner converts common human commands into structured PAIOS actions
without requiring an LLM for routine browser/laptop tasks.

Search semantics:

    Search Python tutorials
        -> global web search

    Search Google for Python tutorials
        -> Google search

    Search YouTube for Python tutorials
        -> open YouTube + site search

    Open YouTube then search Python tutorials
        -> open YouTube + site search

The planner explicitly carries search scope so the browser does not have
to guess based on whatever page happens to be open.
"""

from __future__ import annotations

import re
from typing import Any


class ActionPlanner:

    SITE_ALIASES = {
        "youtube": "https://www.youtube.com",
        "github": "https://github.com",
        "chatgpt": "https://chatgpt.com",
        "linkedin": "https://www.linkedin.com",
        "gmail": "https://mail.google.com",
        "google": "https://www.google.com",
        "bing": "https://www.bing.com",
        "duckduckgo": "https://duckduckgo.com",
        "duck duck go": "https://duckduckgo.com",
        "facebook": "https://www.facebook.com",
        "instagram": "https://www.instagram.com",
        "amazon": "https://www.amazon.in",
        "reddit": "https://www.reddit.com",
        "stackoverflow": "https://stackoverflow.com",
        "stack overflow": "https://stackoverflow.com",
        "python": "https://www.python.org",
        "wikipedia": "https://www.wikipedia.org",
        "npm": "https://www.npmjs.com",
        "npmjs": "https://www.npmjs.com",
        "x": "https://x.com",
        "twitter": "https://x.com",
    }

    SEARCH_ENGINES = {
        "google": "https://www.google.com",
        "bing": "https://www.bing.com",
        "duckduckgo": "https://duckduckgo.com",
        "duck duck go": "https://duckduckgo.com",
    }

    APPS = {
        "chrome": "chrome",
        "google chrome": "chrome",
        "edge": "edge",
        "microsoft edge": "edge",
        "firefox": "firefox",
        "mozilla firefox": "firefox",
        "brave": "brave",
        "brave browser": "brave",
        "notepad": "notepad",
        "calculator": "calculator",
        "calc": "calculator",
        "vscode": "vscode",
        "vs code": "vscode",
        "visual studio code": "vscode",
        "explorer": "explorer",
        "file explorer": "explorer",
        "paint": "paint",
        "powershell": "powershell",
        "terminal": "terminal",
        "command prompt": "cmd",
        "cmd": "cmd",
        "wordpad": "wordpad",
    }

    WRAPPERS = (
        "please ",
        "can you ",
        "could you ",
        "would you ",
        "would you please ",
        "please can you ",
    )

    # ------------------------------------------------------------------
    # NORMALIZATION
    # ------------------------------------------------------------------

    def _normalize(self, message: str) -> str:
        text = str(message or "").strip()

        for wrapper in self.WRAPPERS:
            if text.lower().startswith(wrapper):
                text = text[len(wrapper):].strip()
                break

        text = re.sub(r"\s+", " ", text)

        return text

    # ------------------------------------------------------------------
    # SEQUENTIAL COMMAND SPLITTING
    # ------------------------------------------------------------------

    def _split(self, message: str) -> list[str]:
        """
        Split explicit sequential commands.

        Do NOT split every "and", because queries such as:

            Python and Java tutorials

        are valid single searches.
        """

        # Split explicit sequences and conjunctions only when the
        # following word clearly starts a new command. This preserves
        # natural search queries such as "Python and Java tutorials".
        parts = re.split(
            r"\s+(?:then|and then|after that|next)\s+"
            r"|\s+and\s+(?="
            r"(?:open|launch|start|run|search|look\s+up|find|type|write|press|hit|"
            r"click|tap|fill|hover|select|check|uncheck|scroll|"
            r"go back|go forward|reload|refresh|save|copy|paste|"
            r"undo|redo|show desktop|close|minimize|maximize|"
            r"move|double click|right click|left click)\b)"
            r"|\s*;\s*",
            message,
            flags=re.IGNORECASE,
        )

        return [
            part.strip(" ,.!?")
            for part in parts
            if part.strip(" ,.!?")
        ]

    # ------------------------------------------------------------------
    # URL
    # ------------------------------------------------------------------

    def _url(self, target: str) -> str | None:
        target = target.strip().strip(" .!?")
        low = target.lower()

        if low in self.SITE_ALIASES:
            return self.SITE_ALIASES[low]

        if re.match(r"^https?://", target, re.IGNORECASE):
            return target

        if re.match(
            r"^(?:www\.)?[\w.-]+\.[a-z]{2,}(?:/.*)?$",
            target,
            re.IGNORECASE,
        ):
            return "https://" + target

        return None

    # ------------------------------------------------------------------
    # QUERY CLEANING
    # ------------------------------------------------------------------

    def _clean_query(self, query: str) -> str:
        query = str(query or "").strip()
        query = query.strip("\"'")
        query = re.sub(r"\s+", " ", query)

        return query.strip(" .!?")

    # ------------------------------------------------------------------
    # SITE NAME
    # ------------------------------------------------------------------

    def _canonical_site(self, site: str) -> str:
        low = str(site or "").strip().lower()

        aliases = {
            "duck duck go": "duckduckgo",
            "stack overflow": "stackoverflow",
            "google chrome": "chrome",
            "visual studio code": "vscode",
        }

        return aliases.get(low, low)

    # ------------------------------------------------------------------
    # SEARCH ACTION
    # ------------------------------------------------------------------

    def _search_action(
        self,
        engine: str | None,
        site: str | None,
        query: str,
    ) -> list[dict[str, Any]]:

        query = self._clean_query(query)

        if not query:
            return []

        actions: list[dict[str, Any]] = []

        # --------------------------------------------------------------
        # SITE SEARCH
        # --------------------------------------------------------------

        if site:

            canonical_site = self._canonical_site(site)

            url = self._url(canonical_site)

            if url:

                actions.append(
                    {
                        "action": "open_url",
                        "url": url,
                    }
                )

                actions.append(
                    {
                        "action": "search",
                        "query": query,
                        "scope": "site",
                        "site": canonical_site,
                    }
                )

                return actions

        # --------------------------------------------------------------
        # SEARCH ENGINE
        # --------------------------------------------------------------

        if engine:

            canonical_engine = self._canonical_site(engine)

            url = self.SEARCH_ENGINES.get(
                canonical_engine
            )

            if url:

                actions.append(
                    {
                        "action": "open_url",
                        "url": url,
                    }
                )

                actions.append(
                    {
                        "action": "search",
                        "query": query,
                        "scope": "web",
                        "engine": canonical_engine,
                    }
                )

                return actions

        # --------------------------------------------------------------
        # DEFAULT = GLOBAL WEB SEARCH
        # --------------------------------------------------------------

        return [
            {
                "action": "search",
                "query": query,
                "scope": "web",
                "engine": "auto",
            }
        ]

    # ------------------------------------------------------------------
    # SEARCH PARSER
    # ------------------------------------------------------------------

    def _parse_search(
        self,
        raw: str,
    ) -> list[dict[str, Any]] | None:

        text = raw.strip()

        # ==============================================================
        # SEARCH <SITE> FOR <QUERY>
        # ==============================================================

        match = re.match(
            r"^(?:search|look\s+up|find)\s+"
            r"(?:on\s+)?"
            r"(google|bing|duckduckgo|duck\s+duck\s+go|"
            r"youtube|github|chatgpt|linkedin|gmail|amazon|"
            r"reddit|stackoverflow|stack\s+overflow|"
            r"wikipedia|npm|npmjs)"
            r"\s+(?:for\s+)?(.+)$",
            text,
            re.IGNORECASE,
        )

        if match:

            target = match.group(1).strip()
            query = match.group(2).strip()

            canonical = self._canonical_site(target)

            if canonical in {
                "google",
                "bing",
                "duckduckgo",
            }:

                return self._search_action(
                    engine=canonical,
                    site=None,
                    query=query,
                )

            return self._search_action(
                engine=None,
                site=canonical,
                query=query,
            )

        # ==============================================================
        # GOOGLE <QUERY>
        # BING <QUERY>
        # DUCKDUCKGO <QUERY>
        # ==============================================================

        match = re.match(
            r"^(google|bing|duckduckgo|duck\s+duck\s+go)"
            r"\s+(.+)$",
            text,
            re.IGNORECASE,
        )

        if match:

            return self._search_action(
                engine=self._canonical_site(
                    match.group(1)
                ),
                site=None,
                query=match.group(2),
            )

        # ==============================================================
        # SEARCH THE WEB
        # SEARCH ONLINE
        # SEARCH FOR
        # LOOK UP
        # FIND ONLINE
        # ==============================================================

        match = re.match(
            r"^(?:"
            r"search(?:\s+the)?\s+(?:web|internet|online)"
            r"|search"
            r"|look\s+up"
            r"|web\s+search"
            r"|find\s+online"
            r")"
            r"\s+(?:for\s+)?(.+)$",
            text,
            re.IGNORECASE,
        )

        if match:

            return self._search_action(
                engine="auto",
                site=None,
                query=match.group(1),
            )

        return None

    # ------------------------------------------------------------------
    # APP PARSER
    # ------------------------------------------------------------------

    def _parse_app(
        self,
        raw: str,
    ) -> dict[str, Any] | None:

        match = re.match(
            r"^(?:open|launch|start|run)"
            r"\s+(?:the\s+)?(.+?)\s*$",
            raw,
            re.IGNORECASE,
        )

        if not match:
            return None

        target = match.group(1).strip().strip(" .!?")
        low = target.lower()

        if low in self.APPS:

            return {
                "action": "laptop_open_app",
                "app": self.APPS[low],
            }

        return None

    # ------------------------------------------------------------------
    # WINDOW ACTIONS
    # ------------------------------------------------------------------

    def _parse_window_action(
        self,
        low: str,
    ) -> dict[str, Any] | None:

        match = re.match(
            r"^(close|minimize|maximize)"
            r"\s+(?:the\s+)?(?:current\s+)?"
            r"(?:window|app|application)$",
            low,
        )

        if match:

            return {
                "action": "laptop_" + match.group(1),
            }

        if low in {
            "show desktop",
            "go to desktop",
            "desktop",
            "show the desktop",
        }:

            return {
                "action": "laptop_show_desktop",
            }

        return None

    # ------------------------------------------------------------------
    # LAPTOP BASIC
    # ------------------------------------------------------------------

    def _parse_laptop_basic(
        self,
        raw: str,
        low: str,
    ) -> dict[str, Any] | None:

        if low in {"copy", "copy that"}:
            return {"action": "laptop_copy"}

        if low in {"paste", "paste that"}:
            return {"action": "laptop_paste"}

        if low in {"save", "save it"}:
            return {"action": "laptop_save"}

        if low in {"undo", "undo that"}:
            return {"action": "laptop_undo"}

        if low in {"redo", "redo that"}:
            return {"action": "laptop_redo"}

        if low in {
            "select all",
            "select everything",
        }:

            return {
                "action": "laptop_select_all",
            }

        # --------------------------------------------------------------
        # MOUSE MOVE
        # --------------------------------------------------------------

        match = re.match(
            r"^(?:move|move mouse)"
            r"\s+(?:the\s+mouse\s+)?(?:to\s+)?"
            r"(\d+)\s*[, ]\s*(\d+)$",
            raw,
            re.IGNORECASE,
        )

        if match:

            return {
                "action": "laptop_move",
                "x": int(match.group(1)),
                "y": int(match.group(2)),
            }

        # --------------------------------------------------------------
        # MOUSE CLICK
        # --------------------------------------------------------------

        match = re.match(
            r"^(double\s+click|right\s+click|left\s+click|click)"
            r"(?:\s+at|\s+on)?\s*"
            r"(?:(\d+)\s*[, ]\s*(\d+))?$",
            raw,
            re.IGNORECASE,
        )

        if match:

            action_type = match.group(1).lower()

            if match.group(2):

                return {
                    "action": "laptop_click",
                    "x": int(match.group(2)),
                    "y": int(match.group(3)),
                    "clicks": (
                        2
                        if action_type == "double click"
                        else 1
                    ),
                    "button": (
                        "right"
                        if action_type == "right click"
                        else "left"
                    ),
                }

        # --------------------------------------------------------------
        # TYPE / WRITE
        # --------------------------------------------------------------

        match = re.match(
            r'^(?:type|write|enter)\s+(.+)$',
            raw,
            re.IGNORECASE,
        )

        if match:

            text = match.group(1).strip()

            if text:

                return {
                    "action": "laptop_type",
                    "text": text.strip("\"'"),
                }

        # --------------------------------------------------------------
        # PRESS
        # --------------------------------------------------------------

        match = re.match(
            r"^(?:press|hit)\s+(.+)$",
            raw,
            re.IGNORECASE,
        )

        if match:

            return {
                "action": "laptop_press",
                "key": match.group(1).strip(),
            }

        # --------------------------------------------------------------
        # SCROLL
        # --------------------------------------------------------------

        match = re.match(
            r"^scroll\s+(up|down)"
            r"(?:\s+(\d+))?$",
            raw,
            re.IGNORECASE,
        )

        if match:

            direction = match.group(1).lower()
            amount = int(match.group(2) or 5)

            if direction == "down":
                amount = -abs(amount)
            else:
                amount = abs(amount)

            return {
                "action": "laptop_scroll",
                "amount": amount,
            }

        return None

    # ------------------------------------------------------------------
    # BROWSER NAVIGATION
    # ------------------------------------------------------------------

    def _parse_browser_navigation(
        self,
        raw: str,
        low: str,
    ) -> dict[str, Any] | None:

        if low in {
            "back",
            "go back",
            "browser back",
        }:

            return {
                "action": "back",
            }

        if low in {
            "forward",
            "go forward",
            "browser forward",
        }:

            return {
                "action": "forward",
            }

        if low in {
            "reload",
            "refresh",
            "refresh page",
            "reload page",
        }:

            return {
                "action": "reload",
            }

        if low in {
            "read page",
            "read this page",
            "read webpage",
            "read website",
            "what is on this page",
        }:

            return {
                "action": "read",
            }

        if low in {
            "new tab",
            "open new tab",
            "open a new tab",
        }:

            return {
                "action": "new_tab",
            }

        if low in {
            "close tab",
            "close this tab",
            "close current tab",
        }:

            return {
                "action": "close_tab",
            }

        if low in {
            "show tabs",
            "list tabs",
            "list browser tabs",
        }:

            return {
                "action": "tabs",
            }

        match = re.match(
            r"^(?:switch to|go to)\s+tab\s+(\d+)$",
            low,
        )

        if match:

            return {
                "action": "switch_tab",
                "index": int(match.group(1)),
            }

        return None

    # ------------------------------------------------------------------
    # BROWSER INTERACTION
    # ------------------------------------------------------------------

    def _parse_browser_interaction(
        self,
        raw: str,
        low: str,
    ) -> dict[str, Any] | None:

        # --------------------------------------------------------------
        # CLICK
        # --------------------------------------------------------------

        match = re.match(
            r"^(?:click|tap)\s+(?:on\s+)?(.+)$",
            raw,
            re.IGNORECASE,
        )

        if match:

            return {
                "action": "click",
                "target": match.group(1).strip(),
            }

        # --------------------------------------------------------------
        # FILL
        # --------------------------------------------------------------

        match = re.match(
            r"^fill\s+(?:the\s+)?(.+?)"
            r"\s+(?:with|as)\s+(.+)$",
            raw,
            re.IGNORECASE,
        )

        if match:

            return {
                "action": "fill",
                "target": match.group(1).strip(),
                "text": match.group(2).strip().strip("\"'"),
            }

        # --------------------------------------------------------------
        # TYPE INTO
        # --------------------------------------------------------------

        match = re.match(
            r"^(?:type|write)\s+(?:into|in)\s+(.+?)"
            r"\s+(?:with|as)\s+(.+)$",
            raw,
            re.IGNORECASE,
        )

        if match:

            return {
                "action": "fill",
                "target": match.group(1).strip(),
                "text": match.group(2).strip().strip("\"'"),
            }

        # --------------------------------------------------------------
        # HOVER
        # --------------------------------------------------------------

        match = re.match(
            r"^hover\s+(?:over\s+)?(.+)$",
            raw,
            re.IGNORECASE,
        )

        if match:

            return {
                "action": "hover",
                "target": match.group(1).strip(),
            }

        # --------------------------------------------------------------
        # SELECT
        # --------------------------------------------------------------

        match = re.match(
            r"^(?:select|choose)\s+(.+?)"
            r"\s+(?:in|from)\s+(.+)$",
            raw,
            re.IGNORECASE,
        )

        if match:

            return {
                "action": "select",
                "target": match.group(2).strip(),
                "value": match.group(1).strip(),
            }

        # --------------------------------------------------------------
        # CHECK
        # --------------------------------------------------------------

        match = re.match(
            r"^(?:check|tick)\s+(.+)$",
            raw,
            re.IGNORECASE,
        )

        if match:

            return {
                "action": "check",
                "target": match.group(1).strip(),
            }

        # --------------------------------------------------------------
        # UNCHECK
        # --------------------------------------------------------------

        match = re.match(
            r"^(?:uncheck|untick)\s+(.+)$",
            raw,
            re.IGNORECASE,
        )

        if match:

            return {
                "action": "uncheck",
                "target": match.group(1).strip(),
            }

        # --------------------------------------------------------------
        # WAIT
        # --------------------------------------------------------------

        match = re.match(
            r"^wait\s+(?:for\s+)?"
            r"([\d.]+)\s*(?:seconds?|secs?|s)?$",
            raw,
            re.IGNORECASE,
        )

        if match:

            return {
                "action": "wait",
                "seconds": float(match.group(1)),
            }

        # --------------------------------------------------------------
        # SCREENSHOT
        # --------------------------------------------------------------

        if low.startswith(
            (
                "screenshot",
                "take a screenshot",
                "capture the page",
                "capture screenshot",
            )
        ):

            return {
                "action": "screenshot",
            }

        # --------------------------------------------------------------
        # FIND
        # --------------------------------------------------------------

        match = re.match(
            r"^(?:find|locate)\s+(.+)$",
            raw,
            re.IGNORECASE,
        )

        if match:

            return {
                "action": "find",
                "target": match.group(1).strip(),
            }

        # --------------------------------------------------------------
        # BROWSER SCROLL
        # --------------------------------------------------------------

        match = re.match(
            r"^scroll\s+(down|up)"
            r"(?:\s+(\d+))?"
            r"(?:\s*(?:pixels?|px))?$",
            raw,
            re.IGNORECASE,
        )

        if match:

            direction = match.group(1).lower()
            amount = int(match.group(2) or 700)

            if direction == "up":
                amount = -abs(amount)
            else:
                amount = abs(amount)

            return {
                "action": "scroll",
                "amount": amount,
            }

        return None

    # ------------------------------------------------------------------
    # OPEN
    # ------------------------------------------------------------------

    def _parse_open(
        self,
        raw: str,
    ) -> dict[str, Any] | None:

        match = re.match(
            r"^(?:open|go\s+to|goto|navigate\s+to|visit)"
            r"\s+(.+)$",
            raw,
            re.IGNORECASE,
        )

        if not match:
            return None

        target = match.group(1).strip().strip(" .!?")

        if target.lower() in {
            "first result",
            "the first result",
            "first search result",
            "first result on the page",
        }:

            return {
                "action": "click",
                "target": "first search result",
            }

        url = self._url(target)

        if url:

            return {
                "action": "open_url",
                "url": url,
            }

        return {
            "action": "click",
            "target": target,
        }

    # ------------------------------------------------------------------
    # MAIN PLANNER
    # ------------------------------------------------------------------

    def plan(
        self,
        message: str,
    ) -> list[dict[str, Any]]:

        message = self._normalize(message)

        if not message:
            return []

        output: list[dict[str, Any]] = []

        for segment in self._split(message):

            raw = segment.strip(" ,.!?")
            low = raw.lower()

            if not raw:
                continue

            # ==========================================================
            # 1. SEARCH
            # ==========================================================

            search_actions = self._parse_search(raw)

            if search_actions:

                output.extend(search_actions)
                continue

            # ==========================================================
            # 2. LAPTOP APP
            # ==========================================================

            app_action = self._parse_app(raw)

            if app_action:

                output.append(app_action)
                continue

            # ==========================================================
            # 3. WINDOW
            # ==========================================================

            window_action = self._parse_window_action(low)

            if window_action:

                output.append(window_action)
                continue

            # ==========================================================
            # 4. LAPTOP BASIC
            # ==========================================================

            laptop_action = self._parse_laptop_basic(
                raw,
                low,
            )

            if laptop_action:

                output.append(laptop_action)
                continue

            # ==========================================================
            # 5. BROWSER NAVIGATION
            # ==========================================================

            navigation_action = self._parse_browser_navigation(
                raw,
                low,
            )

            if navigation_action:

                output.append(navigation_action)
                continue

            # ==========================================================
            # 6. BROWSER INTERACTION
            # ==========================================================

            browser_action = self._parse_browser_interaction(
                raw,
                low,
            )

            if browser_action:

                output.append(browser_action)
                continue

            # ==========================================================
            # 7. OPEN URL / SITE / TARGET
            # ==========================================================

            open_action = self._parse_open(raw)

            if open_action:

                output.append(open_action)
                continue

            # ==========================================================
            # 8. UNKNOWN
            # ==========================================================

            output.append(
                {
                    "action": "unknown",
                    "text": raw,
                }
            )

        valid = [
            action
            for action in output
            if action.get("action") != "unknown"
        ]

        if valid:
            return valid

        return [
            {
                "action": "unknown",
                "text": message,
            }
        ]


action_planner = ActionPlanner()