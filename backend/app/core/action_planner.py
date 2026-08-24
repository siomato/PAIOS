import re
import hashlib


class ActionPlanner:

    # =====================================================
    # PLAN
    # =====================================================

    def plan(self, user_message: str):

        message = user_message.strip()

        if not message:
            return []

        # =================================================
        # SITE-SCOPED SEARCH NORMALIZATION
        # =================================================
        #
        # Examples:
        #
        #   On YouTube, search for Python tutorials
        #   On YouTube search for Python tutorials
        #   Search YouTube for Python tutorials
        #   Search Python tutorials on YouTube
        #
        # These are converted into:
        #
        #   Open YouTube and search for Python tutorials
        #
        # This prevents "On YouTube" from becoming:
        #
        #   {'action': 'unknown', ...}
        #
        # =================================================

        message = self._normalize_site_search(
            message
        )

        steps = []

        parts = self._split_commands(
            message
        )

        for part in parts:

            step = part.strip()

            if not step:
                continue

            step = re.sub(
                r"^[,;]+|[,;]+$",
                "",
                step
            ).strip()

            if step.lower().startswith("and "):

                step = step[4:].strip()

            if not step:
                continue

            # -------------------------------------------------
            # Normalize trailing sentence punctuation
            # -------------------------------------------------

            lower_step = re.sub(
                r"[.!?]+$",
                "",
                step.lower()
            ).strip()

            # =================================================
            # SEARCH
            # =================================================

            if lower_step.startswith("search "):

                query = step[7:].strip()

                if query.lower().startswith("for "):

                    query = query[4:].strip()

                if query:

                    steps.append({
                        "action": "search",
                        "query": query
                    })

                continue

            # =================================================
            # CLICK
            # =================================================

            if lower_step.startswith("click "):

                target = step[6:].strip()

                if target:

                    target = self._normalize_click_target(
                        target
                    )

                    steps.append({
                        "action": "click",
                        "target": target
                    })

                continue

            # =================================================
            # OPEN
            # =================================================

            if lower_step.startswith("open "):

                target = step[5:].strip()

                if not target:
                    continue

                target_lower = target.lower()

                # -------------------------------------------------
                # "open first result"
                # -------------------------------------------------

                if target_lower in (
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
                ):

                    steps.append({
                        "action": "click",
                        "target": "first search result"
                    })

                    continue

                # -------------------------------------------------
                # Resolve website
                # -------------------------------------------------

                url = self._resolve_website_url(
                    target
                )

                if url:

                    steps.append({
                        "action": "open_url",
                        "url": url
                    })

                else:

                    steps.append({
                        "action": "click",
                        "target": target
                    })

                continue

            # =================================================
            # GO TO
            # =================================================

            if (
                lower_step.startswith("go to ")
                or
                lower_step.startswith("goto ")
            ):

                if lower_step.startswith("go to "):

                    target = step[6:].strip()

                else:

                    target = step[5:].strip()

                if not target:
                    continue

                url = self._resolve_website_url(
                    target
                )

                if url:

                    steps.append({
                        "action": "open_url",
                        "url": url
                    })

                else:

                    steps.append({
                        "action": "click",
                        "target": target
                    })

                continue

            # =================================================
            # NAVIGATE TO
            # =================================================

            if lower_step.startswith(
                "navigate to "
            ):

                target = step[12:].strip()

                if not target:
                    continue

                url = self._resolve_website_url(
                    target
                )

                if url:

                    steps.append({
                        "action": "open_url",
                        "url": url
                    })

                else:

                    steps.append({
                        "action": "click",
                        "target": target
                    })

                continue

            # =================================================
            # READ
            # =================================================

            if lower_step in (
                "read",
                "read page",
                "read the page",
                "read current page",
                "read the current page",
            ):

                steps.append({
                    "action": "read"
                })

                continue

            # =================================================
            # READ SPECIFIC PAGE
            # =================================================
            #
            # Example:
            #
            #   read the Documentation page
            #
            # becomes:
            #
            #   click Documentation
            #   read
            #
            # =================================================

            page_target_match = re.match(
                r"^read\s+(?:the\s+)?(.+?)\s+page$",
                lower_step,
                flags=re.IGNORECASE
            )

            if page_target_match:

                target = page_target_match.group(
                    1
                ).strip()

                if target:

                    target = self._normalize_click_target(
                        target
                    )

                    steps.append({
                        "action": "click",
                        "target": target
                    })

                    steps.append({
                        "action": "read"
                    })

                continue

            # =================================================
            # FILL
            # =================================================

            if lower_step.startswith("fill "):

                command = step[5:].strip()

                if command:

                    steps.append({
                        "action": "fill",
                        "command": command
                    })

                continue

            # =================================================
            # PRESS
            # =================================================

            if lower_step.startswith("press "):

                # Extract the keyboard key from natural language.
                key = step[6:].strip()

                # Remove sentence punctuation that may be added by
                # voice input or natural-language commands.
                key = re.sub(
                    r"[.,!?;:]+$",
                    "",
                    key
                ).strip()

                # Normalize common keyboard names to Playwright keys.
                key_map = {
                    "enter": "Enter",
                    "return": "Enter",
                    "esc": "Escape",
                    "escape": "Escape",
                    "space": "Space",
                    "spacebar": "Space",
                    "tab": "Tab",
                    "backspace": "Backspace",
                    "delete": "Delete",
                    "del": "Delete",
                    "up": "ArrowUp",
                    "down": "ArrowDown",
                    "left": "ArrowLeft",
                    "right": "ArrowRight",
                    "home": "Home",
                    "end": "End",
                    "page up": "PageUp",
                    "page down": "PageDown",
                }

                key = key_map.get(
                    key.lower(),
                    key
                )

                if key:

                    steps.append({
                        "action": "press",
                        "key": key
                    })

                continue

            # =================================================
            # UNKNOWN
            # =================================================

            steps.append({
                "action": "unknown",
                "command": step
            })

        # =====================================================
        # PLAN METADATA
        # =====================================================

        total_steps = len(steps)

        plan_id = (
            "plan-"
            + hashlib.sha1(
                message.encode("utf-8")
            ).hexdigest()[:12]
        )

        normalized_steps = []

        for index, action in enumerate(
            steps,
            start=1
        ):

            item = dict(action)

            item["step_index"] = index
            item["total_steps"] = total_steps
            item["plan_id"] = plan_id

            normalized_steps.append(
                item
            )

        return normalized_steps

    # =====================================================
    # NORMALIZE SITE-SCOPED SEARCH
    # =====================================================

    def _normalize_site_search(
        self,
        message: str
    ):
        """
        Normalize site-scoped search requests.

        Examples:

            On YouTube, search for Python tutorials

        becomes:

            Open YouTube
            Fill search box with Python tutorials
            Press ENTER
        """

        if not message:
            return message

        text = " ".join(
            message.strip().split()
        )

        # =================================================
        # PATTERN 1
        #
        # On YouTube, search for Python tutorials
        # On YouTube search for Python tutorials
        # =================================================

        match = re.match(
            r"^\s*(?:on|in)\s+"
            r"(.+?)"
            r"\s*,?\s+"
            r"search\s+(?:for\s+)?"
            r"(.+?)"
            r"\s*[.!?]*\s*$",
            text,
            flags=re.IGNORECASE
        )

        if match:
            site = match.group(1).strip()
            query = match.group(2).strip()

            url = self._resolve_website_url(
                site
            )

            if url and query:
                return (
                    f"Open {site} and "
                    f"Fill search box with {query} and "
                    f"Press ENTER"
                )

        # =================================================
        # PATTERN 2
        #
        # Search YouTube for Python tutorials
        # =================================================

        match = re.match(
            r"^\s*search\s+"
            r"(.+?)"
            r"\s+for\s+"
            r"(.+?)"
            r"\s*[.!?]*\s*$",
            text,
            flags=re.IGNORECASE
        )

        if match:
            site = match.group(1).strip()
            query = match.group(2).strip()

            url = self._resolve_website_url(
                site
            )

            if url and query:
                return (
                    f"Open {site}. "
                    f"Fill search box with {query}. "
                    f"Press ENTER"
                )

        # =================================================
        # PATTERN 3
        #
        # Search Python tutorials on YouTube
        # =================================================

        match = re.match(
            r"^\s*search\s+"
            r"(?:for\s+)?"
            r"(.+?)"
            r"\s+on\s+"
            r"(.+?)"
            r"\s*[.!?]*\s*$",
            text,
            flags=re.IGNORECASE
        )

        if match:
            query = match.group(1).strip()
            site = match.group(2).strip()

            url = self._resolve_website_url(
                site
            )

            if url and query:
                return (
                    f"Open {site}. "
                    f"Fill search box with {query}. "
                    f"Press ENTER"
                )

        # =================================================
        # No site-scoped search detected
        # =================================================

        return text

    # =====================================================
    # RESOLVE WEBSITE URL
    # =====================================================

    def _resolve_website_url(
        self,
        target: str
    ):

        if not target:
            return None

        value = target.strip()

        # -------------------------------------------------
        # Remove common natural-language prefixes
        # -------------------------------------------------

        value = re.sub(
            r"^(the\s+)?website\s+",
            "",
            value,
            flags=re.IGNORECASE
        ).strip()

        # -------------------------------------------------
        # Already a full URL
        # -------------------------------------------------

        if re.match(
            r"^https?://",
            value,
            flags=re.IGNORECASE
        ):

            return value

        # -------------------------------------------------
        # www.example.com
        # -------------------------------------------------

        if value.lower().startswith("www."):

            return "https://" + value

        # -------------------------------------------------
        # Known websites
        # -------------------------------------------------

        websites = {

            "google":
                "https://www.google.com",

            "google.com":
                "https://www.google.com",

            "youtube":
                "https://www.youtube.com",

            "youtube.com":
                "https://www.youtube.com",

            "github":
                "https://github.com",

            "github.com":
                "https://github.com",

            "linkedin":
                "https://www.linkedin.com",

            "linkedin.com":
                "https://www.linkedin.com",

            "facebook":
                "https://www.facebook.com",

            "facebook.com":
                "https://www.facebook.com",

            "instagram":
                "https://www.instagram.com",

            "instagram.com":
                "https://www.instagram.com",

            "twitter":
                "https://twitter.com",

            "twitter.com":
                "https://twitter.com",

            "x":
                "https://x.com",

            "x.com":
                "https://x.com",

            "reddit":
                "https://www.reddit.com",

            "reddit.com":
                "https://www.reddit.com",

            "gmail":
                "https://mail.google.com",

            "gmail.com":
                "https://mail.google.com",

            "chatgpt":
                "https://chatgpt.com",

            "chat.openai.com":
                "https://chat.openai.com",

            "openai":
                "https://openai.com",

            "amazon":
                "https://www.amazon.com",

            "amazon.com":
                "https://www.amazon.com",

            "netflix":
                "https://www.netflix.com",

            "netflix.com":
                "https://www.netflix.com",

            "spotify":
                "https://open.spotify.com",

            "spotify.com":
                "https://open.spotify.com",

            "stackoverflow":
                "https://stackoverflow.com",

            "stackoverflow.com":
                "https://stackoverflow.com",

            "python":
                "https://www.python.org",

            "python.org":
                "https://www.python.org",

            "wikipedia":
                "https://www.wikipedia.org",

            "wikipedia.org":
                "https://www.wikipedia.org",
        }

        normalized = value.lower().strip()

        if normalized in websites:

            return websites[
                normalized
            ]

        # -------------------------------------------------
        # Domain-like target
        #
        # Example:
        #
        # python.org
        # example.com
        # docs.python.org
        #
        # -------------------------------------------------

        if re.match(
            r"^[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+$",
            value
        ):

            return "https://" + value

        # -------------------------------------------------
        # Natural-language website names
        #
        # Example:
        #
        # Google website
        # YouTube website
        #
        # -------------------------------------------------

        cleaned = re.sub(
            r"\s+website$",
            "",
            normalized,
            flags=re.IGNORECASE
        ).strip()

        if cleaned in websites:

            return websites[
                cleaned
            ]

        # -------------------------------------------------
        # Not recognized
        # -------------------------------------------------

        return None

    # =====================================================
    # SPLIT COMMANDS
    # =====================================================

    def _split_commands(
        self,
        message: str
    ):

        text = " ".join(
            message.strip().split()
        )

        if not text:
            return []

        # -----------------------------------------------------
        # Supported command boundaries
        # -----------------------------------------------------

        command_start = (
            r"(?:"
            r"search|"
            r"click|"
            r"open|"
            r"go\s+to|"
            r"goto|"
            r"navigate\s+to|"
            r"read(?:\s+(?:the\s+)?)?page|"
            r"read|"
            r"fill|"
            r"press"
            r")"
        )

        # -----------------------------------------------------
        # Normalize:
        #
        # ", and search"
        # ", search"
        # -----------------------------------------------------

        text = re.sub(
            rf"[,;]+\s+and\s+(?={command_start}\b)",
            " and ",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            rf"[,;]+\s*(?={command_start}\b)",
            " and ",
            text,
            flags=re.IGNORECASE
        )

        # -----------------------------------------------------
        # Explicit THEN
        # -----------------------------------------------------

        parts = re.split(
            r"\s+then\s+",
            text,
            flags=re.IGNORECASE
        )

        final_parts = []

        for part in parts:

            part = part.strip()

            if not part:
                continue

            # -------------------------------------------------
            # "and <supported command>" boundaries
            # -------------------------------------------------

            boundary = (
                rf"\s+and\s+(?="
                rf"{command_start}\b"
                rf")"
            )

            pieces = re.split(
                boundary,
                part,
                flags=re.IGNORECASE
            )

            for piece in pieces:

                piece = piece.strip()

                if not piece:
                    continue

                piece = re.sub(
                    r"^[,;]+|[,;]+$",
                    "",
                    piece
                ).strip()

                piece = re.sub(
                    r"^and\s+",
                    "",
                    piece,
                    flags=re.IGNORECASE
                ).strip()

                if piece:

                    final_parts.append(
                        piece
                    )

        return final_parts

    # =====================================================
    # NORMALIZE CLICK TARGET
    # =====================================================

    def _normalize_click_target(
        self,
        target: str
    ):

        normalized = target.strip()

        target_lower = normalized.lower()

        if target_lower in (
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
        ):

            return "first search result"

        return normalized


# =========================================================
# GLOBAL INSTANCE
# =========================================================

action_planner = ActionPlanner()