import re


class ActionPlanner:

    # =====================================================
    # PLAN
    # =====================================================

    def plan(self, user_message: str):

        message = user_message.strip()

        if not message:
            return []

        steps = []

        # =================================================
        # SPLIT MULTI-STEP COMMANDS
        # =================================================
        #
        # Supports:
        #
        # search X then click Y
        # search X and click Y
        # search X and open Y
        #
        # IMPORTANT:
        # We only split "and click/open" when it represents
        # a new browser action.
        # =================================================

        parts = self._split_commands(message)

        for part in parts:

            step = part.strip()

            if not step:
                continue

            # -------------------------------------------------
            # Remove optional leading "and"
            # -------------------------------------------------

            if step.lower().startswith("and "):

                step = step[4:].strip()

            if not step:
                continue

            lower_step = step.lower()

            # =================================================
            # SEARCH
            # =================================================

            if lower_step.startswith("search "):

                query = step[7:].strip()

                # -------------------------------------------------
                # Remove natural "for"
                #
                # Search for Python tutorials
                #
                # becomes:
                #
                # Python tutorials
                # -------------------------------------------------

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

                # -------------------------------------------------
                # Open first result
                # -------------------------------------------------

                target_lower = target.lower()

                if target_lower in (
                    "first result",
                    "first search result",
                    "first search results",
                    "first useful result",
                    "first useful results",
                ):

                    steps.append({
                        "action": "click",
                        "target": "first search result"
                    })

                    continue

                # -------------------------------------------------
                # Open URL
                # -------------------------------------------------

                if (
                    target.startswith("http://")
                    or
                    target.startswith("https://")
                ):

                    steps.append({
                        "action": "open_url",
                        "url": target
                    })

                else:

                    # Treat "open X" as a click target.
                    #
                    # This is safer for browser automation because
                    # "open" normally means selecting something
                    # already visible on the page.
                    steps.append({
                        "action": "click",
                        "target": target
                    })

                continue

            # =================================================
            # READ PAGE
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

        return steps

    # =====================================================
    # SPLIT COMMANDS
    # =====================================================

    def _split_commands(self, message: str):

        text = message.strip()

        if not text:
            return []

        # =================================================
        # FIRST:
        # Split explicit "then"
        # =================================================

        parts = re.split(
            r"\s+then\s+",
            text,
            flags=re.IGNORECASE
        )

        final_parts = []

        # =================================================
        # SECOND:
        # Split "and click" / "and open"
        #
        # Example:
        #
        # Search for Python tutorials and click
        # THIS TARGET DOES NOT EXIST
        #
        # becomes:
        #
        # Search for Python tutorials
        # click THIS TARGET DOES NOT EXIST
        # =================================================

        for part in parts:

            part = part.strip()

            if not part:
                continue

            # -------------------------------------------------
            # Search + click
            # -------------------------------------------------

            match = re.match(
                r"^(.*?)(?:\s+and\s+)(click)\s+(.+)$",
                part,
                flags=re.IGNORECASE
            )

            if match:

                first_part = match.group(1).strip()

                click_target = match.group(3).strip()

                final_parts.append(
                    first_part
                )

                final_parts.append(
                    f"click {click_target}"
                )

                continue

            # -------------------------------------------------
            # Search + open
            # -------------------------------------------------

            match = re.match(
                r"^(.*?)(?:\s+and\s+)(open)\s+(.+)$",
                part,
                flags=re.IGNORECASE
            )

            if match:

                first_part = match.group(1).strip()

                open_target = match.group(3).strip()

                final_parts.append(
                    first_part
                )

                final_parts.append(
                    f"open {open_target}"
                )

                continue

            # -------------------------------------------------
            # Normal command
            # -------------------------------------------------

            final_parts.append(part)

        return final_parts

    # =====================================================
    # NORMALIZE CLICK TARGET
    # =====================================================

    def _normalize_click_target(self, target: str):

        normalized = target.strip()

        target_lower = normalized.lower()

        if target_lower in (
            "first useful result",
            "first result",
            "first search result",
            "first search results",
            "first useful results",
        ):

            return "first search result"

        return normalized


# =========================================================
# GLOBAL INSTANCE
# =========================================================

action_planner = ActionPlanner()