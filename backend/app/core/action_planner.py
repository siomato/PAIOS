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

        steps = []

        parts = self._split_commands(message)

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
            # FIND
            # =================================================

            if lower_step.startswith("find "):

                query = step[5:].strip()

                if query:
                    steps.append({
                        "action": "find",
                        "query": query
                    })

                continue

            # =================================================
            # CLICK
            # =================================================

            if lower_step.startswith("click "):

                target = step[6:].strip()

                if target:
                    target = self._normalize_click_target(target)

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

                url = self._resolve_website_url(target)

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

                url = self._resolve_website_url(target)

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

            if lower_step.startswith("navigate to "):

                target = step[12:].strip()

                if not target:
                    continue

                url = self._resolve_website_url(target)

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
            ):

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

                key = step[6:].strip()

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

        # =================================================
        # PLAN METADATA
        # =================================================

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

            normalized_steps.append(item)

        return normalized_steps

    # =====================================================
    # RESOLVE WEBSITE URL
    # =====================================================

    def _resolve_website_url(self, target: str):

        if not target:
            return None

        value = target.strip()

        value = re.sub(
            r"^(the\s+)?website\s+",
            "",
            value,
            flags=re.IGNORECASE
        ).strip()

        if re.match(
            r"^https?://",
            value,
            flags=re.IGNORECASE
        ):

            return value

        if value.lower().startswith("www."):

            return "https://" + value

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

            return websites[normalized]

        if re.match(
            r"^[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+$",
            value
        ):

            return "https://" + value

        cleaned = re.sub(
            r"\s+website$",
            "",
            normalized,
            flags=re.IGNORECASE
        ).strip()

        if cleaned in websites:

            return websites[cleaned]

        return None

    # =====================================================
    # SPLIT COMMANDS
    # =====================================================

    def _split_commands(self, message: str):

        text = " ".join(
            message.strip().split()
        )

        if not text:
            return []

        # IMPORTANT:
        # FIND is now a supported command.
        command_start = (
            r"(?:search|click|open|find|go\s+to|goto|"
            r"navigate\s+to|read(?:\s+(?:the\s+)?)?page|"
            r"read|fill|press)"
        )

        # Normalize comma/semicolon before commands.
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

        # Explicit THEN.
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
                    final_parts.append(piece)

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