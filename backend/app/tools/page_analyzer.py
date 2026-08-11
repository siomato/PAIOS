from app.tools.browser_automation import browser_automation


class PageAnalyzer:

    # =====================================================
    # GET INTERACTIVE ELEMENTS
    # =====================================================

    def get_elements(self):

        page = browser_automation.start()

        elements = []

        # -------------------------------------------------
        # Links
        # -------------------------------------------------

        links = page.locator("a").all()

        for index, link in enumerate(links):

            try:

                text = link.inner_text().strip()

                href = link.get_attribute("href")

                if not text:

                    continue

                elements.append({
                    "index": len(elements),
                    "type": "link",
                    "text": text[:200],
                    "href": href,
                })

            except Exception:

                continue

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        buttons = page.locator("button").all()

        for button in buttons:

            try:

                text = button.inner_text().strip()

                if not text:

                    continue

                elements.append({
                    "index": len(elements),
                    "type": "button",
                    "text": text[:200],
                    "href": None,
                })

            except Exception:

                continue

        # -------------------------------------------------
        # Inputs
        # -------------------------------------------------

        inputs = page.locator(
            "input, textarea"
        ).all()

        for element in inputs:

            try:

                placeholder = (
                    element.get_attribute("placeholder")
                    or ""
                )

                name = (
                    element.get_attribute("name")
                    or ""
                )

                element_type = (
                    element.get_attribute("type")
                    or "text"
                )

                elements.append({
                    "index": len(elements),
                    "type": "input",
                    "text": placeholder or name,
                    "href": None,
                    "input_type": element_type,
                })

            except Exception:

                continue

        return elements

    # =====================================================
    # PRINT ELEMENTS
    # =====================================================

    def print_elements(self):

        elements = self.get_elements()

        print(
            "\n========== PAGE ELEMENTS =========="
        )

        for element in elements[:100]:

            print(
                f"[{element['index']}] "
                f"{element['type']} | "
                f"{element['text']}"
            )

            if element.get("href"):

                print(
                    f"    → {element['href']}"
                )

        print(
            "====================================\n"
        )

        return elements


page_analyzer = PageAnalyzer()