# ============================================================
# app/core/replanner.py
#
# PAIOS REPLANNER - RELIABLE VERSION
# ============================================================

import hashlib
import re
from urllib.parse import urlparse


class Replanner:
    """Deterministic recovery planner for browser actions.

    The replanner never uses an LLM. It converts malformed/unknown actions
    into the closest supported browser action and preserves the remaining
    objective whenever a complete plan is available.
    """

    SUPPORTED_ACTIONS = {
        "open_url",
        "search",
        "click",
        "find",
        "read",
        "fill",
        "press",
    }

    def __init__(self):
        print("🧠 REPLANNER MODULE LOADED 🧠")

    def _failure_text(self, failure):
        if failure is None:
            return ""
        if isinstance(failure, dict):
            parts = []
            for key in ("error", "reason", "message", "status"):
                value = failure.get(key)
                if value is not None:
                    parts.append(str(value))
            return " ".join(parts).strip().lower()
        return str(failure).strip().lower()

    def _copy_action(self, action):
        return dict(action) if isinstance(action, dict) else None

    def _metadata(self, actions, original_plan):
        actions = [self._copy_action(a) for a in actions if isinstance(a, dict)]
        actions = [a for a in actions if a is not None]

        plan_id = None
        for item in original_plan or []:
            if isinstance(item, dict) and item.get("plan_id"):
                plan_id = item["plan_id"]
                break

        if not plan_id:
            digest = hashlib.sha1(
                repr(original_plan).encode("utf-8")
            ).hexdigest()[:12]
            plan_id = f"replan-{digest}"

        total = len(actions)
        result = []
        for index, action in enumerate(actions, start=1):
            item = dict(action)
            item["plan_id"] = plan_id
            item["step_index"] = index
            item["total_steps"] = total
            item["replanned"] = True
            result.append(item)
        return result

    def _command_text(self, action):
        if not isinstance(action, dict):
            return ""
        values = []
        for key in ("command", "target", "query", "url", "text", "value", "key"):
            value = action.get(key)
            if value is not None:
                values.append(str(value))
        return " ".join(values).strip()

    def _extract_url(self, text):
        match = re.search(r"https?://[^\s,]+", text, re.I)
        return match.group(0).rstrip(".,)]") if match else None

    def _normalize_unknown(self, action):
        """Convert an unknown/malformed action into a supported action."""
        if not isinstance(action, dict):
            return None, "Invalid action."

        command = self._command_text(action)
        text = command.lower()
        url = action.get("url") or self._extract_url(command)

        if url:
            return {"action": "open_url", "url": url}, "Recovered URL navigation from command."

        # Explicit action synonyms.
        if any(word in text for word in ("read the page", "read page", "read the current page", "tell me what", "summarize the page")):
            return {"action": "read"}, "Recovered page-read intent from command."

        if re.search(r"\bfind\b|\bsearch for\b|\blook for\b|\blocate\b", text):
            query = action.get("query")
            if not query:
                match = re.search(r"(?:find|search for|look for|locate)\s+(.+?)(?:[.!?]|$)", command, re.I)
                query = match.group(1).strip() if match else command
            return {"action": "find", "query": query}, "Recovered find intent from command."

        if re.search(r"\bclick\b|\bselect\b|\bopen the\b", text):
            target = action.get("target")
            if not target:
                match = re.search(r"(?:click|select|open(?: the)?)\s+(.+?)(?:[.!?]|$)", command, re.I)
                target = match.group(1).strip() if match else command
            return {"action": "click", "target": target}, "Recovered click intent from command."

        if re.search(r"\btype\b|\bfill\b|\benter\b", text):
            command_value = action.get("command") or action.get("text") or action.get("value")
            if command_value:
                return {"action": "fill", "command": str(command_value)}, "Recovered fill intent from command."

        if re.search(r"\bpress\b|\bkey\b", text):
            key = action.get("key")
            if not key:
                match = re.search(r"(?:press|key)\s+(.+?)(?:[.!?]|$)", command, re.I)
                key = match.group(1).strip() if match else None
            if key:
                return {"action": "press", "key": key}, "Recovered key-press intent from command."

        if command:
            return {"action": "read"}, "Unknown action; re-read the current page to re-establish context."

        return None, "Unable to recover malformed action."

    def replan_action(self, action, failure):
        print("\n========== REPLANNING ==========")
        print(f"Failed action: {action}")
        print(f"Failure: {failure}")

        if not isinstance(action, dict):
            return {"status": "failed", "error": "Invalid action format.", "actions": []}

        action_type = str(action.get("action") or "unknown").strip().lower()
        failure_text = self._failure_text(failure)

        # Unknown/malformed action is the critical recovery path.
        if action_type not in self.SUPPORTED_ACTIONS:
            recovered, reason = self._normalize_unknown(action)
            if recovered is None:
                return {"status": "failed", "error": reason, "actions": []}
            print(f"🔧 Normalized unknown action → {recovered}")
            return {"status": "success", "reason": reason, "actions": [recovered]}

        if action_type == "open_url":
            url = str(action.get("url") or "").strip()
            if not url:
                return {"status": "failed", "error": "Open URL is empty.", "actions": []}
            try:
                domain = urlparse(url).netloc or urlparse(url).path or url
            except Exception:
                domain = url
            if any(x in failure_text for x in ("timeout", "navigation", "browser", "failed", "network")):
                return {
                    "status": "success",
                    "reason": "Direct navigation failed; search for the destination instead.",
                    "actions": [{"action": "search", "query": domain}],
                }
            return {"status": "success", "reason": "Retry URL navigation after recovery.", "actions": [dict(action)]}

        if action_type == "search":
            query = str(action.get("query") or "").strip()
            if not query:
                return {"status": "failed", "error": "Search query is empty.", "actions": []}
            return {"status": "success", "reason": "Retry search using the browser search path.", "actions": [{"action": "search", "query": query}]}

        if action_type == "click":
            target = str(action.get("target") or "").strip()
            if not target:
                return {"status": "failed", "error": "Click target is empty.", "actions": []}
            lower = target.lower()
            if lower in {"first result", "the first result", "first search result", "the first search result", "first useful result", "the first useful result"}:
                actions = [{"action": "read"}, {"action": "click", "target": "first search result"}]
            else:
                actions = [{"action": "read"}, {"action": "click", "target": target}]
            return {"status": "success", "reason": "Re-read the current page before retrying the click target.", "actions": actions}

        if action_type == "find":
            query = str(action.get("query") or "").strip()
            if not query:
                return {"status": "failed", "error": "Find query is empty.", "actions": []}
            return {"status": "success", "reason": "Re-read the current page before finding the target.", "actions": [{"action": "read"}, {"action": "find", "query": query}]}

        if action_type == "read":
            return {"status": "success", "reason": "Retry reading the current page.", "actions": [{"action": "read"}]}

        if action_type == "fill":
            command = str(action.get("command") or action.get("text") or action.get("value") or "").strip()
            if not command:
                return {"status": "failed", "error": "Fill command is empty.", "actions": []}
            return {"status": "success", "reason": "Re-establish page context before filling.", "actions": [{"action": "read"}, {"action": "fill", "command": command}]}

        if action_type == "press":
            key = str(action.get("key") or "").strip()
            if not key:
                return {"status": "failed", "error": "Press key is empty.", "actions": []}
            return {"status": "success", "reason": "Re-establish page context before pressing the key.", "actions": [{"action": "press", "key": key}]}

        return {"status": "failed", "error": f"No replanning strategy for action: {action_type}", "actions": []}

    def replan(self, original_steps, failed_step, failure):
        print("\n========================================")
        print("          🧠 REPLANNER")
        print("========================================")

        if not isinstance(original_steps, list) or not original_steps:
            return {"status": "failed", "error": "Original plan is empty or invalid.", "steps": []}
        if not isinstance(failed_step, int) or failed_step < 1 or failed_step > len(original_steps):
            return {"status": "failed", "error": "Failed step is outside the plan.", "steps": []}

        failed_action = original_steps[failed_step - 1]
        print(f"Failed step: {failed_step}")
        print(f"Failed action: {failed_action}")

        result = self.replan_action(failed_action, failure)
        if result.get("status") != "success":
            return {"status": "failed", "error": result.get("error", "Replanner failed."), "steps": []}

        new_actions = result.get("actions") or []
        if not new_actions:
            return {"status": "failed", "error": "Replanner generated no alternative actions.", "steps": []}

        # Preserve the remaining original objective after the failed step.
        remaining_steps = original_steps[failed_step:]
        new_plan = list(new_actions) + list(remaining_steps)

        # Remove an immediate exact retry if the alternative contains no
        # different action before it.
        if len(new_plan) > 1 and isinstance(new_plan[0], dict) and isinstance(failed_action, dict):
            same = all(
                new_plan[0].get(k) == failed_action.get(k)
                for k in ("action", "target", "query", "url", "command", "key")
            )
            if same and len(new_actions) == 1:
                return {
                    "status": "failed",
                    "error": "Replanner produced the same failed action.",
                    "steps": [],
                }

        new_plan = self._metadata(new_plan, original_steps)

        print("\n📋 New plan:")
        for index, step in enumerate(new_plan, start=1):
            print(f"  {index}. {step}")

        return {
            "status": "success",
            "reason": result.get("reason"),
            "steps": new_plan,
            "failed_step": failed_step,
        }


replanner = Replanner()