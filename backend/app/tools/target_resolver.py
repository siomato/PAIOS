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

        # Remove punctuation
        text = re.sub(
            r"[.!?,;:]+$",
            "",
            text
        ).strip()

        # Remove common action prefixes
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

        # Remove articles
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

        # -----------------------------------------------------
        # IMPORTANT FIX
        #
        # "Downloads link"
        #       ↓
        # "Downloads"
        #
        # "Login button"
        #       ↓
        # "Login"
        #
        # "Settings tab"
        #       ↓
        # "Settings"
        # -----------------------------------------------------

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

        return text


    # =========================================================
    # SEARCH RESULTS
    # =========================================================

    def _resolve_first_search_result(self):

        results = (
            browser_automation
            .get_search_results()
        )

        if not results:
            return None

        return results[0]


    def _resolve_last_search_result(self):

        results = (
            browser_automation
            .get_search_results()
        )

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

        results = (
            browser_automation
            .get_search_results()
        )

        if (
            number < 1 or
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

        results = (
            browser_automation
            .get_search_results()
        )

        if not results:
            return None

        target_words = set(
            instruction.split()
        )

        best_result = None
        best_score = 0

        for result in results:

            text = (
                result.get("text")
                or result.get("title")
                or ""
            ).lower()

            words = set(
                text.split()
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

    def _target_candidates(self, normalized: str):
        """Return semantic candidates for natural-language targets."""

        candidates = []

        def add(value):
            value = " ".join(str(value).casefold().split()).strip()
            if value and value not in candidates:
                candidates.append(value)

        add(normalized)

        aliases = {
            "documentation page": [
                "documentation",
                "docs",
                "python documentation",
            ],
            "documentation": [
                "docs",
                "python documentation",
            ],
            "download page": [
                "downloads",
                "download",
            ],
            "home page": [
                "home",
                "python",
            ],
        }

        for alias in aliases.get(normalized, []):
            add(alias)

        simplified = re.sub(
            r"\b(page|link|button|tab|menu|option|item|element)\b",
            " ",
            normalized,
        )
        add(simplified)

        return candidates


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

        if (
            normalized == "first result"
            or
            normalized == "first search result"
        ):

            result = (
                self._resolve_first_search_result()
            )

            if result:
                print(
                    "✅ First search result resolved"
                )

            return result


        if (
            normalized == "last result"
            or
            normalized == "last search result"
        ):

            result = (
                self._resolve_last_search_result()
            )

            if result:
                print(
                    "✅ Last search result resolved"
                )

            return result


        numbered = (
            self._resolve_numbered_result(
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


        target_candidates = self._target_candidates(
            normalized
        )

        print(
            f"🎯 Target candidates: {target_candidates}"
        )

        target_word_sets = {
            candidate: set(
                re.findall(
                    r"[a-z0-9]+",
                    candidate
                )
            )
            for candidate in target_candidates
        }

        target_words = list(
            target_word_sets.get(
                normalized,
                set()
            )
        )


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
                    text.casefold().split()
                )
            )

            if candidate_text in target_candidates:

                print(
                    f"🎯 Analyzer exact match: {text}"
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

            for words in target_word_sets.values():
                if (
                    words
                    and
                    all(
                        word in candidate_words
                        for word in words
                    )
                ):
                    alias_match = True
                    break

            if alias_match:

                print(
                    f"🎯 Analyzer word match: {text}"
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

            selectors = [

                "a[href]",

                "button",

                "[role='link']",

                "[role='button']",

                "input[type='button']",

                "input[type='submit']",

            ]


            best_candidate = None
            best_data = None
            best_score = 0


            for selector in selectors:

                try:

                    elements = (
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


                for element in elements:

                    try:

                        if not element.is_visible():
                            continue


                        # -------------------------------------------------
                        # COLLECT CANDIDATE DATA
                        # -------------------------------------------------

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


                        aria = (
                            element
                            .get_attribute(
                                "aria-label"
                            )
                            or ""
                        )


                        title = (
                            element
                            .get_attribute(
                                "title"
                            )
                            or ""
                        )


                        value = (
                            element
                            .get_attribute(
                                "value"
                            )
                            or ""
                        )


                        href = (
                            element
                            .get_attribute(
                                "href"
                            )
                            or ""
                        )


                        # -------------------------------------------------
                        # CANDIDATE VALUES
                        # -------------------------------------------------

                        values = [

                            visible_text,

                            text_content,

                            aria,

                            title,

                            value,

                            href,

                        ]


                        local_score = 0
                        matched_value = ""


                        # -------------------------------------------------
                        # SCORE
                        # -------------------------------------------------

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

                            # Score the original target first, then
                            # semantic aliases such as "docs".
                            for candidate_index, target_candidate in enumerate(
                                target_candidates
                            ):

                                words = target_word_sets.get(
                                    target_candidate,
                                    set()
                                )

                                if not words:
                                    continue

                                if candidate == target_candidate:

                                    candidate_score = (
                                        100
                                        if candidate_index == 0
                                        else 98
                                    )

                                elif all(
                                    word in candidate_words
                                    for word in words
                                ):

                                    candidate_score = (
                                        95
                                        if candidate_index == 0
                                        else 93
                                    )

                                elif target_candidate in candidate:

                                    candidate_score = (
                                        90
                                        if candidate_index == 0
                                        else 88
                                    )

                                elif len(words) == 1 and any(
                                    word in candidate_words
                                    for word in words
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


                        # -------------------------------------------------
                        # DOMAIN-AWARE DOCUMENTATION PREFERENCE
                        # -------------------------------------------------

                        if (
                            normalized == "documentation page"
                            and
                            href
                            and
                            "docs.python.org" in href.casefold()
                        ):
                            score = max(score, 99)

                        # -------------------------------------------------
                        # SAVE BEST
                        # -------------------------------------------------

                        if (
                            local_score >
                            best_score
                        ):

                            try:

                                tag = (
                                    element
                                    .evaluate(
                                        "(el) => el.tagName"
                                    )
                                    .lower()
                                )

                            except Exception:

                                tag = ""


                            best_score = (
                                local_score
                            )

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

                                "tag":
                                    tag,

                            }


                    except Exception:

                        continue


            # =================================================
            # CANDIDATE RESULT
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
                    f"   text : "
                    f"{best_data['text']}"
                )

                print(
                    f"   href : "
                    f"{best_data['href']}"
                )

                print(
                    f"   tag  : "
                    f"{best_data['tag']}"
                )


                # -------------------------------------------------
                # LINK
                # -------------------------------------------------

                if best_data["href"]:

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

                        "type": "link",

                        "text":
                            best_data["text"],

                        "href":
                            href,

                        "aria-label":
                            best_data["aria-label"],

                        "title":
                            best_data["title"],

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

                        "type": "button",

                        "text":
                            best_data["text"],

                        "aria-label":
                            best_data["aria-label"],

                        "title":
                            best_data["title"],

                    }


        # =====================================================
        # SEARCH RESULT FALLBACK
        # =====================================================

        search_match = (
            self._resolve_from_search_results(
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

        return None


# =============================================================
# GLOBAL INSTANCE
# =============================================================

target_resolver = TargetResolver()