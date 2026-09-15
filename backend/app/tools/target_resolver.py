import re
from urllib.parse import urljoin

from app.tools.page_analyzer import page_analyzer
from app.tools.browser_automation import browser_automation


print("🔥 TARGET RESOLVER V2 LOADED 🔥")


class TargetResolver:

    # =========================================================
    # NORMALIZE TARGET
    # =========================================================

    def _normalize(self, instruction: str):

        if not instruction:
            return ""

        text = str(instruction).lower().strip()

        # Remove punctuation from the end.
        text = re.sub(
            r"[.!?,;:]+$",
            "",
            text
        ).strip()

        # Remove common action prefixes.
        prefixes = [
            "click on ",
            "click the ",
            "click ",
            "press ",
            "select ",
            "choose ",
            "tap ",
            "open ",
            "go to ",
        ]

        changed = True

        while changed:

            changed = False

            for prefix in prefixes:

                if text.startswith(prefix):

                    text = text[
                        len(prefix):
                    ].strip()

                    changed = True
                    break

        # Remove leading articles.
        for prefix in (
            "the ",
            "a ",
            "an ",
        ):

            if text.startswith(prefix):

                text = text[
                    len(prefix):
                ].strip()

                break

        # Remove common target suffixes.
        suffixes = [
            " link",
            " button",
            " tab",
            " menu",
            " option",
            " item",
            " element",
        ]

        for suffix in suffixes:

            if text.endswith(suffix):

                text = text[
                    :-len(suffix)
                ].strip()

                break

        # Normalize whitespace.
        text = " ".join(
            text.split()
        )

        return text


    # =========================================================
    # SEARCH RESULTS
    # =========================================================

    def _resolve_first_search_result(self):

        try:

            results = (
                browser_automation
                .get_search_results()
            )

        except Exception:

            return None

        if not results:
            return None

        return results[0]


    def _resolve_last_search_result(self):

        try:

            results = (
                browser_automation
                .get_search_results()
            )

        except Exception:

            return None

        if not results:
            return None

        return results[-1]


    def _resolve_numbered_result(
        self,
        instruction
    ):

        match = re.search(
            r"(?:result|link)\s+(\d+)",
            instruction
        )

        if not match:
            return None

        number = int(
            match.group(1)
        )

        try:

            results = (
                browser_automation
                .get_search_results()
            )

        except Exception:

            return None

        if (
            number < 1
            or
            number > len(results)
        ):

            return None

        return results[
            number - 1
        ]


    # =========================================================
    # SEARCH RESULT MATCH
    # =========================================================

    def _resolve_from_search_results(
        self,
        instruction
    ):

        try:

            results = (
                browser_automation
                .get_search_results()
            )

        except Exception:

            return None

        if not results:
            return None

        target_words = set(
            re.findall(
                r"[a-z0-9]+",
                instruction.casefold()
            )
        )

        best_result = None
        best_score = 0

        for result in results:

            text = (
                result.get("text")
                or result.get("title")
                or ""
            ).casefold()

            words = set(
                re.findall(
                    r"[a-z0-9]+",
                    text
                )
            )

            score = len(
                target_words &
                words
            )

            if score > best_score:

                best_score = score
                best_result = result

        return best_result


    # =========================================================
    # TARGET CANDIDATES / SEMANTIC ALIASES
    # =========================================================

    def _target_candidates(
        self,
        normalized: str
    ):
        """
        Return semantic candidates for
        natural-language targets.
        """

        candidates = []


        def add(value):

            value = (
                " ".join(
                    str(value)
                    .casefold()
                    .split()
                )
                .strip()
            )

            if (
                value
                and
                value not in candidates
            ):

                candidates.append(value)


        add(normalized)


        aliases = {

            # -------------------------------------------------
            # SEARCH
            # -------------------------------------------------

            "search": [
                "search",
                "search box",
                "search field",
                "search input",
                "search bar",
                "search textbox",
                "search form",
            ],

            "search box": [
                "search",
                "search box",
                "search field",
                "search input",
                "search bar",
                "search textbox",
                "search form",
            ],

            "search field": [
                "search",
                "search box",
                "search field",
                "search input",
                "search bar",
                "search textbox",
                "search form",
            ],

            "search input": [
                "search",
                "search box",
                "search field",
                "search input",
                "search bar",
                "search textbox",
                "search form",
            ],

            "search bar": [
                "search",
                "search box",
                "search field",
                "search input",
                "search bar",
                "search textbox",
                "search form",
            ],

            "search textbox": [
                "search",
                "search box",
                "search field",
                "search input",
                "search bar",
                "search textbox",
            ],

            # -------------------------------------------------
            # DOCUMENTATION
            # -------------------------------------------------

            "documentation page": [
                "documentation",
                "docs",
                "python documentation",
            ],

            "documentation": [
                "docs",
                "python documentation",
            ],

            "docs": [
                "documentation",
                "python documentation",
            ],

            # -------------------------------------------------
            # DOWNLOAD
            # -------------------------------------------------

            "download page": [
                "downloads",
                "download",
            ],

            "downloads": [
                "download",
                "downloads",
            ],

            # -------------------------------------------------
            # HOME
            # -------------------------------------------------

            "home page": [
                "home",
                "python",
            ],

            "home": [
                "home",
            ],

            # -------------------------------------------------
            # COMMON BUTTONS
            # -------------------------------------------------

            "login": [
                "login",
                "log in",
                "sign in",
            ],

            "log in": [
                "login",
                "log in",
                "sign in",
            ],

            "sign in": [
                "sign in",
                "login",
            ],

            "submit": [
                "submit",
                "submit button",
            ],

        }


        for alias in aliases.get(
            normalized,
            []
        ):

            add(alias)


        # Remove generic target words.
        simplified = re.sub(
            r"\b("
            r"page|"
            r"link|"
            r"button|"
            r"tab|"
            r"menu|"
            r"option|"
            r"item|"
            r"element|"
            r"field|"
            r"input|"
            r"box|"
            r"bar|"
            r"textbox"
            r")\b",
            " ",
            normalized
        )

        add(simplified)


        return candidates


    # =========================================================
    # ATTRIBUTE HELPERS
    # =========================================================

    def _get_attribute(
        self,
        element,
        name
    ):

        try:

            return (
                element
                .get_attribute(name)
                or ""
            ).strip()

        except Exception:

            return ""


    def _get_tag(
        self,
        element
    ):

        try:

            return (
                element
                .evaluate(
                    "(el) => el.tagName"
                )
                .lower()
            )

        except Exception:

            return ""


    def _build_selector(
        self,
        element,
        tag,
        element_id,
        name,
        aria,
        placeholder,
        input_type
    ):
        """
        Build a stable CSS selector.

        Priority:
            1. unique id
            2. name
            3. aria-label
            4. placeholder
            5. input type
            6. generic tag
        """

        try:

            if element_id:

                escaped_id = (
                    element_id
                    .replace("\\", "\\\\")
                    .replace('"', '\\"')
                )

                locator = element.page.locator(
                    f'#{escaped_id}'
                )

                if locator.count() == 1:

                    return f'#{escaped_id}'

        except Exception:

            pass


        if tag == "input":

            if name:

                try:

                    locator = (
                        element.page
                        .locator(
                            f'input[name="{name}"]'
                        )
                    )

                    if locator.count() == 1:

                        return (
                            f'input[name="{name}"]'
                        )

                except Exception:

                    pass


            if aria:

                try:

                    locator = (
                        element.page
                        .locator(
                            f'input[aria-label="{aria}"]'
                        )
                    )

                    if locator.count() == 1:

                        return (
                            f'input[aria-label="{aria}"]'
                        )

                except Exception:

                    pass


            if placeholder:

                try:

                    locator = (
                        element.page
                        .locator(
                            f'input[placeholder="{placeholder}"]'
                        )
                    )

                    if locator.count() == 1:

                        return (
                            f'input[placeholder="{placeholder}"]'
                        )

                except Exception:

                    pass


            if input_type:

                try:

                    locator = (
                        element.page
                        .locator(
                            f'input[type="{input_type}"]'
                        )
                    )

                    if locator.count() == 1:

                        return (
                            f'input[type="{input_type}"]'
                        )

                except Exception:

                    pass


            return "input"


        if tag == "textarea":

            if name:

                return (
                    f'textarea[name="{name}"]'
                )

            return "textarea"


        if tag == "button":

            if element_id:

                return f'button#{element_id}'

            return "button"


        if tag == "a":

            if element_id:

                return f'a#{element_id}'

            return "a"


        if aria:

            return (
                f'[aria-label="{aria}"]'
            )


        if name:

            return (
                f'[name="{name}"]'
            )


        return (
            tag
            if tag
            else "*"
        )


    # =========================================================
    # SPECIAL INPUT DETECTION
    # =========================================================

    def _is_search_element(
        self,
        tag,
        role,
        input_type,
        aria,
        placeholder,
        name,
        element_id,
        title
    ):

        combined = " ".join(
            [
                aria,
                placeholder,
                name,
                element_id,
                title,
                role,
            ]
        ).casefold()

        search_words = (
            "search",
            "query",
            "find",
        )

        has_search_word = any(
            word in combined
            for word in search_words
        )

        if role.casefold() == "searchbox":
            return True

        if (
            input_type.casefold()
            == "search"
        ):
            return True

        if (
            tag in {
                "input",
                "textarea",
            }
            and
            has_search_word
        ):
            return True

        return False


    # =========================================================
    # MAIN RESOLVER
    # =========================================================

    def resolve(
        self,
        instruction: str
    ):

        print(
            "\n========== TARGET RESOLVER V2 =========="
        )

        print(
            f"🎯 Raw target: {instruction}"
        )


        normalized = self._normalize(
            instruction
        )


        print(
            f"🎯 Normalized target: {normalized}"
        )


        if not normalized:

            print(
                "❌ Empty target"
            )

            return None


        # =====================================================
        # SPECIAL SEARCH TARGETS
        # =====================================================

        if normalized in {
            "first result",
            "first search result",
        }:

            result = (
                self
                ._resolve_first_search_result()
            )

            if result:

                print(
                    "✅ First search result resolved"
                )

            return result


        if normalized in {
            "last result",
            "last search result",
        }:

            result = (
                self
                ._resolve_last_search_result()
            )

            if result:

                print(
                    "✅ Last search result resolved"
                )

            return result


        numbered = (
            self
            ._resolve_numbered_result(
                normalized
            )
        )


        if numbered:

            return numbered


        # =====================================================
        # PAGE ANALYZER
        # =====================================================

        try:

            elements = (
                page_analyzer
                .get_elements()
            )

        except Exception as e:

            print(
                f"⚠️ Page analyzer failed: {e}"
            )

            elements = []


        target_candidates = (
            self
            ._target_candidates(
                normalized
            )
        )


        print(
            f"🎯 Target candidates: "
            f"{target_candidates}"
        )


        target_word_sets = {

            candidate: set(
                re.findall(
                    r"[a-z0-9]+",
                    candidate
                )
            )

            for candidate
            in target_candidates

        }


        # =====================================================
        # PAGE ANALYZER EXACT MATCH
        # =====================================================

        for element in elements:

            text = (
                element.get("text")
                or ""
            ).strip()


            if not text:
                continue


            candidate_text = (
                " ".join(
                    text
                    .casefold()
                    .split()
                )
            )


            if (
                candidate_text
                in target_candidates
            ):

                # For a semantic search-box request, an exact text match
                # such as the YouTube "Search" BUTTON is not the target.
                # The user asked for the editable search field. Defer to
                # the live-DOM resolver so it can select the actual input.
                if normalized in {
                    "search",
                    "search box",
                    "search field",
                    "search input",
                    "search bar",
                    "search textbox",
                }:
                    element_type = str(
                        element.get("type")
                        or element.get("tag")
                        or element.get("role")
                        or ""
                    ).casefold()

                    if element_type in {
                        "button",
                        "submit",
                    }:
                        continue

                print(
                    f"🎯 Analyzer exact match: "
                    f"{text}"
                )

                return element


        # =====================================================
        # PAGE ANALYZER WORD MATCH
        # =====================================================

        for element in elements:

            text = (
                element.get("text")
                or ""
            ).strip()


            if not text:
                continue


            candidate_words = set(
                re.findall(
                    r"[a-z0-9]+",
                    text.casefold()
                )
            )


            alias_match = False


            for words in (
                target_word_sets.values()
            ):

                if (
                    words
                    and
                    all(
                        word
                        in candidate_words
                        for word
                        in words
                    )
                ):

                    alias_match = True
                    break


            if alias_match:

                # Same protection for semantic search-box requests: do not
                # resolve a visible Search button when the requested target
                # is the editable search field.
                if normalized in {
                    "search",
                    "search box",
                    "search field",
                    "search input",
                    "search bar",
                    "search textbox",
                }:
                    element_type = str(
                        element.get("type")
                        or element.get("tag")
                        or element.get("role")
                        or ""
                    ).casefold()

                    if element_type in {
                        "button",
                        "submit",
                    }:
                        continue

                print(
                    f"🎯 Analyzer word match: "
                    f"{text}"
                )

                return element


        # =====================================================
        # LIVE DOM RESOLUTION
        # =====================================================

        print(
            f"🔎 Live DOM resolution for: "
            f"{normalized}"
        )


        try:

            page = (
                browser_automation
                .start()
            )

        except Exception as e:

            print(
                f"⚠️ Browser unavailable: {e}"
            )

            page = None


        if page is not None:

            # -------------------------------------------------
            # IMPORTANT:
            #
            # The old resolver did not inspect normal inputs.
            #
            # This is the main reason:
            #
            #     click the search box
            #
            # produced:
            #
            #     Best DOM score: 0
            #
            # -------------------------------------------------

            selectors = [

                # Links.
                "a[href]",

                # Buttons.
                "button",

                # ARIA links/buttons.
                "[role='link']",
                "[role='button']",

                # Search/textbox controls.
                "[role='textbox']",
                "[role='searchbox']",

                # ALL inputs.
                "input",

                # Text areas.
                "textarea",

                # Content editable.
                "[contenteditable='true']",

                # Explicit button inputs.
                "input[type='button']",
                "input[type='submit']",

            ]


            best_candidate = None
            best_data = None
            best_score = 0


            for selector in selectors:

                try:

                    dom_elements = (
                        page
                        .locator(selector)
                        .all()
                    )

                except Exception as e:

                    print(
                        f"⚠️ DOM scan failed "
                        f"for {selector}: {e}"
                    )

                    continue


                for element in dom_elements:

                    try:

                        if not element.is_visible():
                            continue


                        # =================================================
                        # COLLECT DOM DATA
                        # =================================================

                        visible_text = ""

                        try:

                            visible_text = (
                                element
                                .inner_text()
                                .strip()
                            )

                        except Exception:

                            pass


                        text_content = ""

                        try:

                            text_content = (
                                element
                                .text_content()
                                or ""
                            ).strip()

                        except Exception:

                            pass


                        aria = self._get_attribute(
                            element,
                            "aria-label"
                        )

                        title = self._get_attribute(
                            element,
                            "title"
                        )

                        value = self._get_attribute(
                            element,
                            "value"
                        )

                        href = self._get_attribute(
                            element,
                            "href"
                        )

                        placeholder = (
                            self
                            ._get_attribute(
                                element,
                                "placeholder"
                            )
                        )

                        name = (
                            self
                            ._get_attribute(
                                element,
                                "name"
                            )
                        )

                        element_id = (
                            self
                            ._get_attribute(
                                element,
                                "id"
                            )
                        )

                        role = (
                            self
                            ._get_attribute(
                                element,
                                "role"
                            )
                        )

                        input_type = (
                            self
                            ._get_attribute(
                                element,
                                "type"
                            )
                        )


                        tag = self._get_tag(
                            element
                        )


                        # =================================================
                        # BUILD SEARCH VALUES
                        # =================================================

                        values = [

                            visible_text,
                            text_content,

                            aria,
                            title,
                            value,

                            href,

                            placeholder,
                            name,
                            element_id,

                            role,
                            input_type,

                        ]


                        local_score = 0
                        matched_value = ""


                        # =================================================
                        # STANDARD SCORING
                        # =================================================

                        for value_text in values:

                            if not value_text:
                                continue


                            candidate = (
                                " ".join(
                                    str(
                                        value_text
                                    )
                                    .casefold()
                                    .split()
                                )
                            )


                            if not candidate:
                                continue


                            candidate_words = set(
                                re.findall(
                                    r"[a-z0-9]+",
                                    candidate
                                )
                            )


                            score = 0


                            for (
                                candidate_index,
                                target_candidate
                            ) in enumerate(
                                target_candidates
                            ):

                                words = (
                                    target_word_sets
                                    .get(
                                        target_candidate,
                                        set()
                                    )
                                )


                                if not words:
                                    continue


                                # Exact match.
                                if (
                                    candidate
                                    ==
                                    target_candidate
                                ):

                                    candidate_score = (
                                        100
                                        if candidate_index == 0
                                        else 98
                                    )


                                # All target words exist.
                                elif all(
                                    word
                                    in candidate_words
                                    for word
                                    in words
                                ):

                                    candidate_score = (
                                        95
                                        if candidate_index == 0
                                        else 93
                                    )


                                # Target phrase contained.
                                elif (
                                    target_candidate
                                    in candidate
                                ):

                                    candidate_score = (
                                        90
                                        if candidate_index == 0
                                        else 88
                                    )


                                # Single-word match.
                                elif (
                                    len(words) == 1
                                    and
                                    any(
                                        word
                                        in candidate_words
                                        for word
                                        in words
                                    )
                                ):

                                    candidate_score = 75


                                else:

                                    candidate_score = 0


                                score = max(
                                    score,
                                    candidate_score
                                )


                            if score > local_score:

                                local_score = score

                                matched_value = (
                                    value_text
                                )


                        # =================================================
                        # SEARCH BOX SPECIAL MATCH
                        # =================================================

                        if normalized in {
                            "search",
                            "search box",
                            "search field",
                            "search input",
                            "search bar",
                            "search textbox",
                        }:

                            if self._is_search_element(
                                tag=tag,
                                role=role,
                                input_type=input_type,
                                aria=aria,
                                placeholder=placeholder,
                                name=name,
                                element_id=element_id,
                                title=title,
                            ):

                                # Strong preference for an actual
                                # search control.
                                local_score = max(
                                    local_score,
                                    120
                                )

                                matched_value = (
                                    aria
                                    or
                                    placeholder
                                    or
                                    name
                                    or
                                    element_id
                                    or
                                    "search"
                                )


                        # =================================================
                        # TEXTBOX SPECIAL MATCH
                        # =================================================

                        if normalized in {
                            "textbox",
                            "text box",
                            "text field",
                            "input",
                        }:

                            if (
                                tag
                                in {
                                    "input",
                                    "textarea",
                                }
                                or
                                role
                                in {
                                    "textbox",
                                    "searchbox",
                                }
                            ):

                                local_score = max(
                                    local_score,
                                    110
                                )


                        # =================================================
                        # DOCUMENTATION PREFERENCE
                        # =================================================

                        if (
                            normalized
                            ==
                            "documentation page"
                            and
                            href
                            and
                            "docs.python.org"
                            in href.casefold()
                        ):

                            local_score = max(
                                local_score,
                                99
                            )


                        # =================================================
                        # BUILD SELECTOR
                        # =================================================

                        selector_for_element = ""

                        try:

                            # ID is the most reliable option.
                            if element_id:

                                selector_for_element = (
                                    f'#{element_id}'
                                )

                                try:

                                    count = (
                                        page
                                        .locator(
                                            selector_for_element
                                        )
                                        .count()
                                    )

                                    if count != 1:

                                        selector_for_element = ""

                                except Exception:

                                    selector_for_element = ""


                            # Name.
                            if (
                                not selector_for_element
                                and
                                name
                            ):

                                selector_for_element = (
                                    f'{tag}[name="{name}"]'
                                )

                                try:

                                    count = (
                                        page
                                        .locator(
                                            selector_for_element
                                        )
                                        .count()
                                    )

                                    if count != 1:

                                        selector_for_element = ""

                                except Exception:

                                    selector_for_element = ""


                            # ARIA label.
                            if (
                                not selector_for_element
                                and
                                aria
                            ):

                                selector_for_element = (
                                    f'{tag}[aria-label="{aria}"]'
                                )

                                try:

                                    count = (
                                        page
                                        .locator(
                                            selector_for_element
                                        )
                                        .count()
                                    )

                                    if count != 1:

                                        selector_for_element = ""

                                except Exception:

                                    selector_for_element = ""


                            # Placeholder.
                            if (
                                not selector_for_element
                                and
                                placeholder
                            ):

                                selector_for_element = (
                                    f'{tag}[placeholder="{placeholder}"]'
                                )

                                try:

                                    count = (
                                        page
                                        .locator(
                                            selector_for_element
                                        )
                                        .count()
                                    )

                                    if count != 1:

                                        selector_for_element = ""

                                except Exception:

                                    selector_for_element = ""


                            # Role.
                            if (
                                not selector_for_element
                                and
                                role
                            ):

                                selector_for_element = (
                                    f'{tag}[role="{role}"]'
                                )

                                try:

                                    count = (
                                        page
                                        .locator(
                                            selector_for_element
                                        )
                                        .count()
                                    )

                                    if count != 1:

                                        selector_for_element = ""

                                except Exception:

                                    selector_for_element = ""


                            # Input type.
                            if (
                                not selector_for_element
                                and
                                tag == "input"
                                and
                                input_type
                            ):

                                selector_for_element = (
                                    f'input[type="{input_type}"]'
                                )


                            # Generic fallback.
                            if not selector_for_element:

                                selector_for_element = (
                                    tag
                                    if tag
                                    else "*"
                                )


                        except Exception:

                            selector_for_element = (
                                tag
                                if tag
                                else "*"
                            )


                        # =================================================
                        # SAVE BEST
                        # =================================================

                        if local_score > best_score:

                            best_score = local_score

                            best_candidate = (
                                element
                            )

                            best_data = {

                                "text":
                                    visible_text
                                    or
                                    matched_value,

                                "href":
                                    href,

                                "aria-label":
                                    aria,

                                "title":
                                    title,

                                "placeholder":
                                    placeholder,

                                "name":
                                    name,

                                "id":
                                    element_id,

                                "role":
                                    role,

                                "type":
                                    input_type,

                                "tag":
                                    tag,

                                "selector":
                                    selector_for_element,

                            }


                    except Exception:

                        continue


            # =================================================
            # RESULT
            # =================================================

            print(
                f"🎯 Best DOM score: "
                f"{best_score}"
            )


            if (
                best_candidate is not None
                and
                best_data is not None
                and
                best_score >= 70
            ):

                print(
                    "✅ LIVE DOM TARGET RESOLVED"
                )

                print(
                    f"   text       : "
                    f"{best_data['text']}"
                )

                print(
                    f"   href       : "
                    f"{best_data['href']}"
                )

                print(
                    f"   tag        : "
                    f"{best_data['tag']}"
                )

                print(
                    f"   role       : "
                    f"{best_data['role']}"
                )

                print(
                    f"   placeholder: "
                    f"{best_data['placeholder']}"
                )

                print(
                    f"   selector   : "
                    f"{best_data['selector']}"
                )


                # -------------------------------------------------
                # LINK
                # -------------------------------------------------

                if (
                    best_data["href"]
                    and
                    best_data["tag"] == "a"
                ):

                    href = (
                        best_data["href"]
                    )


                    try:

                        href = urljoin(
                            page.url,
                            href
                        )

                    except Exception:

                        pass


                    return {

                        "type":
                            "link",

                        "text":
                            best_data["text"],

                        "href":
                            href,

                        "aria-label":
                            best_data[
                                "aria-label"
                            ],

                        "title":
                            best_data[
                                "title"
                            ],

                        "selector":
                            best_data[
                                "selector"
                            ],

                    }


                # -------------------------------------------------
                # BUTTON
                # -------------------------------------------------

                if (
                    best_data["tag"]
                    ==
                    "button"
                ):

                    return {

                        "type":
                            "button",

                        "text":
                            best_data["text"],

                        "aria-label":
                            best_data[
                                "aria-label"
                            ],

                        "title":
                            best_data[
                                "title"
                            ],

                        "selector":
                            best_data[
                                "selector"
                            ],

                    }


                # -------------------------------------------------
                # INPUT / SEARCHBOX / TEXTAREA
                # -------------------------------------------------

                if (
                    best_data["tag"]
                    in {
                        "input",
                        "textarea",
                    }
                    or
                    best_data["role"]
                    in {
                        "textbox",
                        "searchbox",
                    }
                ):

                    return {

                        "type":
                            "input",

                        "text":
                            best_data["text"],

                        "placeholder":
                            best_data[
                                "placeholder"
                            ],

                        "name":
                            best_data["name"],

                        "id":
                            best_data["id"],

                        "aria-label":
                            best_data[
                                "aria-label"
                            ],

                        "title":
                            best_data["title"],

                        "role":
                            best_data["role"],

                        "input_type":
                            best_data["type"],

                        "selector":
                            best_data[
                                "selector"
                            ],

                    }


                # -------------------------------------------------
                # GENERIC ELEMENT
                # -------------------------------------------------

                return {

                    "type":
                        "element",

                    "text":
                        best_data["text"],

                    "aria-label":
                        best_data[
                            "aria-label"
                        ],

                    "title":
                        best_data["title"],

                    "selector":
                        best_data[
                            "selector"
                        ],

                }


        # =====================================================
        # SEARCH RESULT FALLBACK
        # =====================================================

        search_match = (
            self
            ._resolve_from_search_results(
                normalized
            )
        )


        if search_match:

            print(
                "✅ Search-result fallback resolved"
            )

            return search_match


        # =====================================================
        # FAILURE
        # =====================================================

        print(
            f"❌ Could not resolve target: "
            f"{instruction}"
        )

        # -----------------------------------------------------
        # DEFINITIVE TARGET MISS
        #
        # Returning structured failure information allows the
        # click pipeline / recovery engine to distinguish an
        # actually missing target from a temporary DOM problem.
        # This prevents wasting all 7 retry attempts when the
        # resolver has exhausted its strategies.
        # -----------------------------------------------------

        return {
            "type": "unresolved_target",
            "target": instruction,
            "score": best_score,
            "recoverable": False,
            "definitive": True,
        }


# =============================================================
# GLOBAL INSTANCE
# =============================================================

target_resolver = TargetResolver()