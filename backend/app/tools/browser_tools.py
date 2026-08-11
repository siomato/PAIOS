from app.tools.browser_automation import browser_automation
from app.tools.target_resolver import target_resolver


class BrowserTools:

    # =====================================================
    # OPEN URL
    # =====================================================

    def open_url(self, url: str):

        return browser_automation.open_url(url)

    # =====================================================
    # GOOGLE SEARCH
    # =====================================================

    def search(self, query: str):

        return browser_automation.search(
        query
    )

    # =====================================================
    # CLICK
    # =====================================================

    def click(self, target: str):

        print(
            "\n========== CLICK TARGET =========="
        )

        print(
            f"Target: {target}"
        )

        # -------------------------------------------------
        # Resolve natural-language target
        # -------------------------------------------------

        resolved = target_resolver.resolve(
            target
        )

        print(
            f"Resolved target: {resolved}"
        )

        # -------------------------------------------------
        # Target could not be resolved
        # -------------------------------------------------

        if not resolved:

            raise RuntimeError(
                f"Could not resolve target: {target}"
            )

        # -------------------------------------------------
        # Link
        # -------------------------------------------------

        if resolved.get("type") == "link":

            href = resolved.get(
                "href"
            )

            text = resolved.get(
                "text",
                ""
            )

            print(
                f"🔗 Link text: {text}"
            )

            print(
                f"🌐 Link href: {href}"
            )

            if not href:

                raise RuntimeError(
                    f"Resolved link has no href: "
                    f"{resolved}"
                )

            # Use href directly.
            #
            # This is more reliable than trying to
            # reconstruct a CSS selector from text.

            result = browser_automation.open_url(
                href
            )

            if isinstance(result, str):

                if (
                    "failed" in result.lower()
                    or "error" in result.lower()
                ):

                    raise RuntimeError(
                        result
                    )

            return (
                f"Clicked target: {text}"
            )

        # -------------------------------------------------
        # Button
        # -------------------------------------------------

        if resolved.get("type") == "button":

            text = resolved.get(
                "text",
                ""
            )

            print(
                f"🔘 Button: {text}"
            )

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
                        == text.lower()
                    ):

                        button.click()

                        return (
                            f"Clicked target: {text}"
                        )

                except Exception:

                    continue

            raise RuntimeError(
                f"Button not found: {text}"
            )

        # -------------------------------------------------
        # Input
        # -------------------------------------------------

        if resolved.get("type") == "input":

            raise RuntimeError(
                "Input targets cannot be "
                "clicked through the current "
                "click pipeline."
            )

        # -------------------------------------------------
        # Unknown target type
        # -------------------------------------------------

        raise RuntimeError(
            f"Unsupported target type: "
            f"{resolved.get('type')}"
        )

    # =====================================================
    # FILL
    # =====================================================

    def fill_from_command(
        self,
        command: str
    ):

        if " with " not in command:

            raise ValueError(
                "Invalid fill command. "
                "Use: fill <selector> with <text>"
            )

        selector, text = command.split(
            " with ",
            1
        )

        selector = selector.strip()
        text = text.strip()

        if not selector:

            raise ValueError(
                "Selector cannot be empty."
            )

        if not text:

            raise ValueError(
                "Text cannot be empty."
            )

        return browser_automation.fill(
            selector,
            text
        )

    # =====================================================
    # PRESS
    # =====================================================

    def press_key(
        self,
        key: str
    ):

        if not key:

            raise ValueError(
                "Key cannot be empty."
            )

        return browser_automation.press(
            "body",
            key
        )

    # =====================================================
    # READ PAGE
    # =====================================================

    def read_page(self):

        result = browser_automation.read_page()

        if isinstance(result, dict):

            if result.get("error"):

                raise RuntimeError(
                    result["error"]
                )

        return result

    # =====================================================
    # WEBSITES
    # =====================================================

    def open_youtube(self):

        return self.open_url(
            "https://www.youtube.com"
        )

    def open_chatgpt(self):

        return self.open_url(
            "https://chat.openai.com"
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


# =========================================================
# GLOBAL INSTANCE
# =========================================================

browser_tools = BrowserTools()