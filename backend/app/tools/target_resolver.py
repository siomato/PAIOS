from app.tools.page_analyzer import page_analyzer
from app.tools.browser_automation import browser_automation


print("🔥 TARGET RESOLVER MODULE LOADED 🔥")


class TargetResolver:

    # =========================================================
    # NORMALIZE INSTRUCTION
    # =========================================================

    def _normalize(self, instruction: str):

        if not instruction:

            return ""

        instruction = (
            instruction
            .lower()
            .strip()
        )

        # Remove common filler words
        prefixes = [
            "the ",
            "a ",
            "an ",
        ]

        for prefix in prefixes:

            if instruction.startswith(prefix):

                instruction = (
                    instruction[
                        len(prefix):
                    ]
                    .strip()
                )

        return instruction

    # =========================================================
    # RESOLVE FIRST SEARCH RESULT
    # =========================================================

    def _resolve_first_search_result(
        self
    ):

        print(
            "🔎 Resolving first search result..."
        )

        results = (
            browser_automation
            .get_search_results()
        )

        print(
            f"📋 Search result candidates: "
            f"{len(results)}"
        )

        if not results:

            print(
                "⚠️ No stored search results."
            )

            return None

        result = results[0]

        print(
            f"🎯 Resolved first result: "
            f"{result.get('title', '')}"
        )

        return result

    # =========================================================
    # RESOLVE LAST SEARCH RESULT
    # =========================================================

    def _resolve_last_search_result(
        self
    ):

        print(
            "🔎 Resolving last search result..."
        )

        results = (
            browser_automation
            .get_search_results()
        )

        print(
            f"📋 Search result candidates: "
            f"{len(results)}"
        )

        if not results:

            print(
                "⚠️ No stored search results."
            )

            return None

        result = results[-1]

        print(
            f"🎯 Resolved last result: "
            f"{result.get('title', '')}"
        )

        return result

    # =========================================================
    # RESOLVE NUMBERED RESULT
    # =========================================================

    def _resolve_numbered_result(
        self,
        instruction
    ):

        import re

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

        print(
            f"📋 Search result candidates: "
            f"{len(results)}"
        )

        if number < 1:

            return None

        if number > len(results):

            print(
                f"⚠️ Result {number} "
                f"is unavailable."
            )

            return None

        result = results[
            number - 1
        ]

        print(
            f"🎯 Resolved result {number}: "
            f"{result.get('title', '')}"
        )

        return result

    # =========================================================
    # RESOLVE BY SEARCH RESULT TITLE
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

        instruction_words = set(
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

            if not text:

                continue

            words = set(
                text.split()
            )

            score = len(
                instruction_words
                & words
            )

            if score > best_score:

                best_score = score
                best_result = result

        if best_result:

            print(
                f"🎯 Best search-result match: "
                f"{best_result.get('title', '')}"
            )

        return best_result

    # =========================================================
    # RESOLVE
    # =========================================================

    def resolve(
        self,
        instruction: str
    ):

        print(
            "\n========== TARGET RESOLVER =========="
        )

        print(
            f"Target instruction: {instruction}"
        )

        normalized = self._normalize(
            instruction
        )

        print(
            f"Normalized target: {normalized}"
        )

        if not normalized:

            print(
                "❌ Empty target."
            )

            return None

        # =====================================================
        # FIRST SEARCH RESULT
        # =====================================================

        if (
            normalized == "first result"
            or normalized == "first search result"
            or "first search result" in normalized
        ):

            result = (
                self._resolve_first_search_result()
            )

            if result:

                print(
                    "✅ Search target resolved."
                )

            else:

                print(
                    "❌ Could not resolve "
                    "first search result."
                )

            return result

        # =====================================================
        # LAST SEARCH RESULT
        # =====================================================

        if (
            normalized == "last result"
            or normalized == "last search result"
            or "last search result" in normalized
        ):

            result = (
                self._resolve_last_search_result()
            )

            if result:

                print(
                    "✅ Search target resolved."
                )

            else:

                print(
                    "❌ Could not resolve "
                    "last search result."
                )

            return result

        # =====================================================
        # NUMBERED RESULT
        # =====================================================

        numbered = (
            self._resolve_numbered_result(
                normalized
            )
        )

        if numbered:

            return numbered

        # =====================================================
        # PAGE ELEMENTS
        #
        # IMPORTANT:
        # We only retrieve page elements AFTER
        # checking search-result targets.
        #
        # This fixes the previous bug where:
        #
        # if not elements:
        #     return None
        #
        # happened before "first search result".
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

        # =====================================================
        # EXACT TEXT MATCH
        # =====================================================

        for element in elements:

            text = (
                element.get("text")
                or ""
            ).strip()

            if not text:

                continue

            if (
                normalized
                == text.lower().strip()
            ):

                print(
                    f"🎯 Exact match found: "
                    f"{text}"
                )

                return element

        # =====================================================
        # PARTIAL TEXT MATCH
        # =====================================================

        instruction_words = (
            normalized.split()
        )

        for element in elements:

            text = (
                element.get("text")
                or ""
            ).strip()

            if not text:

                continue

            text_lower = (
                text.lower()
            )

            if all(
                word in text_lower
                for word in instruction_words
            ):

                print(
                    f"🎯 Partial match found: "
                    f"{text}"
                )

                return element

        # =====================================================
        # SEARCH RESULT FUZZY MATCH
        # =====================================================

        search_match = (
            self._resolve_from_search_results(
                normalized
            )
        )

        if search_match:

            return search_match

        # =====================================================
        # NO MATCH
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