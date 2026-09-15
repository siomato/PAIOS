"""
============================================================
PAIOS / ULTRON
RELIABILITY TEST HARNESS
============================================================

Runs real end-to-end commands through AgentController.run().

The harness itself does not modify ULTRON.
It only measures the existing system.

============================================================
"""

import sys
import time
import traceback
from pathlib import Path


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )


# ============================================================
# REAL ULTRON ENTRY POINT
# ============================================================

from app.core.agent_controller import AgentController


# ============================================================
# TEST CONFIGURATION
# ============================================================

TESTS = [

    {
        "name": "Basic Navigation",
        "command": (
            "Open https://www.python.org"
        ),
        "expected": "success",
    },

    {
        "name": "Click",
        "command": (
            "Open https://www.python.org "
            "and click Downloads."
        ),
        "expected": "success",
    },

    {
        "name": "Search",
        "command": (
            "Open https://www.wikipedia.org "
            "and search for Quantum computing."
        ),
        "expected": "success",
    },

    {
        "name": "Multi Step",
        "command": (
            "Open https://www.python.org "
            "and go to Documentation."
        ),
        "expected": "success",
    },

    {
        "name": "Tanglish",
        "command": (
            "Python.org open panni "
            "Documentation click pannu."
        ),
        "expected": "success",
    },

    {
        "name": "Intentional Failure",
        "command": (
            "Open https://www.python.org "
            "and click XYZ_NON_EXISTENT_BUTTON."
        ),
        "expected": "failure",
    },
]


# ============================================================
# DISPLAY
# ============================================================

def print_header():

    print()
    print("=" * 60)
    print("        🧪 PAIOS RELIABILITY TEST")
    print("=" * 60)
    print()


def print_separator():

    print("-" * 60)


def print_result(
    index,
    name,
    status,
    duration
):

    icon = (
        "✅"
        if status == "PASS"
        else "❌"
    )

    print(
        f"{index:<3} "
        f"{icon} "
        f"{name:<28} "
        f"{status:<6} "
        f"{duration:>7.2f}s"
    )


# ============================================================
# RESULT INTERPRETATION
# ============================================================

def extract_status(result):

    if result is None:
        return None

    if isinstance(
        result,
        bool
    ):
        return (
            "completed"
            if result
            else "failed"
        )

    if isinstance(
        result,
        dict
    ):

        for key in (
            "status",
            "task_status",
            "result_status"
        ):

            value = result.get(
                key
            )

            if value is not None:

                return str(
                    value
                ).lower()

        return None

    # --------------------------------------------------------
    # AgentState-like object
    # --------------------------------------------------------

    status = getattr(
        result,
        "status",
        None
    )

    if status is not None:

        return str(
            status
        ).lower()

    return None


# ============================================================
# SUCCESS DETECTION
# ============================================================

def is_success(result):

    status = extract_status(
        result
    )

    if status in (
        "complete",
        "completed",
        "success",
        "successful",
        "done"
    ):

        return True

    if isinstance(
        result,
        bool
    ):

        return result

    if isinstance(
        result,
        dict
    ):

        if result.get(
            "success"
        ) is True:

            return True

    return False


# ============================================================
# FAILURE DETECTION
# ============================================================

def is_failure(result):

    status = extract_status(
        result
    )

    if status in (
        "failed",
        "failure",
        "error",
        "aborted"
    ):

        return True

    if isinstance(
        result,
        dict
    ):

        if result.get(
            "success"
        ) is False:

            return True

        if result.get(
            "failed_step"
        ) is not None:

            return True

    return False


# ============================================================
# SINGLE TEST
# ============================================================

def run_test(
    controller,
    test,
    index
):

    name = test["name"]

    command = test["command"]

    expected = test["expected"]

    print()
    print_separator()

    print(
        f"🧪 TEST {index}: {name}"
    )

    print(
        f"💬 Command: {command}"
    )

    print(
        f"🎯 Expected: {expected}"
    )

    print_separator()

    start_time = time.perf_counter()

    try:

        # ----------------------------------------------------
        # REAL ULTRON EXECUTION
        # ----------------------------------------------------

        result = controller.run(
            command
        )

        duration = (
            time.perf_counter()
            - start_time
        )

        print()
        print(
            "📦 Controller result:"
        )

        print(
            result
        )

        # ====================================================
        # EXPECTED SUCCESS
        # ====================================================

        if expected == "success":

            if is_success(
                result
            ):

                print(
                    "✅ Expected successful "
                    "execution confirmed."
                )

                return {
                    "name": name,
                    "status": "PASS",
                    "duration": duration,
                }

            print(
                "❌ Expected success, "
                "but completion was not confirmed."
            )

            return {
                "name": name,
                "status": "FAIL",
                "duration": duration,
            }

        # ====================================================
        # EXPECTED FAILURE
        # ====================================================

        if expected == "failure":

            if is_failure(
                result
            ):

                print(
                    "🛡️ Safe failure confirmed."
                )

                return {
                    "name": name,
                    "status": "PASS",
                    "duration": duration,
                    "expected_failure": True,
                }

            print(
                "❌ Expected ULTRON to fail "
                "safely, but failure was not confirmed."
            )

            return {
                "name": name,
                "status": "FAIL",
                "duration": duration,
                "expected_failure": True,
            }

        # ----------------------------------------------------
        # Unknown expectation
        # ----------------------------------------------------

        raise ValueError(
            f"Unknown expected result: {expected}"
        )

    except Exception as exc:

        duration = (
            time.perf_counter()
            - start_time
        )

        print()
        print(
            "❌ TEST EXCEPTION"
        )

        print(
            f"Error: {exc}"
        )

        traceback.print_exc()

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # An exception is NOT automatically a PASS for the
        # intentional failure test.
        #
        # We only pass it if the controller itself reports
        # a controlled failure result.
        # ----------------------------------------------------

        return {
            "name": name,
            "status": "FAIL",
            "duration": duration,
            "exception": str(exc),
        }


# ============================================================
# MAIN
# ============================================================

def main():

    print_header()

    # --------------------------------------------------------
    # Create ONE controller for the entire test suite.
    #
    # This is important because we want to test the same
    # lifecycle ULTRON uses during normal operation.
    # --------------------------------------------------------

    print(
        "🤖 Creating AgentController..."
    )

    controller = AgentController()

    print(
        "✅ AgentController ready."
    )

    results = []

    suite_start = (
        time.perf_counter()
    )

    # ========================================================
    # RUN TESTS
    # ========================================================

    for index, test in enumerate(
        TESTS,
        start=1
    ):

        result = run_test(
            controller,
            test,
            index
        )

        results.append(
            result
        )

        print_result(
            index,
            result["name"],
            result["status"],
            result["duration"]
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    total_duration = (
        time.perf_counter()
        - suite_start
    )

    total = len(
        results
    )

    passed = sum(
        1
        for result in results
        if result["status"] == "PASS"
    )

    failed = (
        total
        - passed
    )

    success_rate = (
        (passed / total) * 100
        if total
        else 0
    )

    print()
    print("=" * 60)
    print("                 📊 SUMMARY")
    print("=" * 60)

    print(
        f"TOTAL TESTS    : {total}"
    )

    print(
        f"PASSED         : {passed}"
    )

    print(
        f"FAILED         : {failed}"
    )

    print(
        f"SUCCESS RATE   : {success_rate:.2f}%"
    )

    print(
        f"TOTAL TIME     : {total_duration:.2f}s"
    )

    print("=" * 60)

    # ========================================================
    # RELIABILITY CLASSIFICATION
    # ========================================================

    if success_rate == 100:

        print(
            "🟢 RELIABILITY STATUS: EXCELLENT"
        )

    elif success_rate >= 80:

        print(
            "🟡 RELIABILITY STATUS: NEEDS HARDENING"
        )

    else:

        print(
            "🔴 RELIABILITY STATUS: UNSTABLE"
        )

    print("=" * 60)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()