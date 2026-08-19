import threading
import queue
import traceback


class BrowserWorker:

    def __init__(self):
        self._queue = queue.Queue()

        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
            name="PAIOS-BrowserWorker"
        )

        self._started = False
        self._start_lock = threading.Lock()

    # =========================================================
    # START WORKER
    # =========================================================

    def start(self):

        with self._start_lock:

            if not self._started:

                print(
                    "🧵 Starting PAIOS BrowserWorker..."
                )

                self._started = True

                self._thread.start()

                print(
                    "✅ PAIOS BrowserWorker started."
                )

    # =========================================================
    # WORKER LOOP
    # =========================================================

    def _run(self):

        print(
            "🧵 BrowserWorker thread running."
        )

        while True:

            function, args, kwargs, result_queue = (
                self._queue.get()
            )

            function_name = getattr(
                function,
                "__name__",
                str(function)
            )

            print(
                f"\n⚙️ BrowserWorker executing: "
                f"{function_name}"
            )

            try:

                result = function(
                    *args,
                    **kwargs
                )

                print(
                    f"✅ BrowserWorker completed: "
                    f"{function_name}"
                )

                result_queue.put({
                    "success": True,
                    "result": result
                })

            except Exception as e:

                print(
                    f"❌ BrowserWorker error in "
                    f"{function_name}: {e}"
                )

                traceback.print_exc()

                result_queue.put({
                    "success": False,
                    "error": e
                })

            finally:

                self._queue.task_done()

    # =========================================================
    # EXECUTE
    # =========================================================

    def execute(
        self,
        function,
        *args,
        timeout=60,
        **kwargs
    ):

        # -----------------------------------------------------
        # Prevent a worker-thread deadlock
        # -----------------------------------------------------

        if (
            threading.current_thread()
            is self._thread
        ):

            print(
                "⚠️ BrowserWorker.execute() called "
                "from BrowserWorker thread."
            )

            return function(
                *args,
                **kwargs
            )

        # -----------------------------------------------------
        # Start worker
        # -----------------------------------------------------

        self.start()

        # -----------------------------------------------------
        # Result queue
        # -----------------------------------------------------

        result_queue = queue.Queue(
            maxsize=1
        )

        # -----------------------------------------------------
        # Queue task
        # -----------------------------------------------------

        self._queue.put(
            (
                function,
                args,
                kwargs,
                result_queue
            )
        )

        function_name = getattr(
            function,
            "__name__",
            str(function)
        )

        print(
            f"📥 Task queued: {function_name}"
        )

        # -----------------------------------------------------
        # Wait with bounded timeout
        # -----------------------------------------------------

        try:

            response = result_queue.get(
                timeout=timeout
            )

        except queue.Empty:

            raise TimeoutError(
                f"BrowserWorker timeout after "
                f"{timeout}s while executing "
                f"'{function_name}'."
            )

        # -----------------------------------------------------
        # Worker reported an exception
        # -----------------------------------------------------

        if not response["success"]:

            raise response["error"]

        # -----------------------------------------------------
        # Success
        # -----------------------------------------------------

        return response["result"]


# =============================================================
# GLOBAL INSTANCE
# =============================================================

browser_worker = BrowserWorker()