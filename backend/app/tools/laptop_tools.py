"""Windows-friendly laptop automation with explicit capability checks.

PAIOS LaptopTools
-----------------
Provides controlled Windows GUI automation with:
- application launching
- foreground-window activation
- keyboard input
- mouse input
- clipboard operations
- screenshots
- filesystem helpers

The important execution guarantee is:

    open_app()
        -> wait for application
        -> locate its window
        -> bring it to foreground

    type_text()
        -> re-activate last opened application
        -> wait briefly
        -> type into the active application
"""

from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import time
from pathlib import Path

from app.security.access_control import access_controller, AccessDenied

try:
    import pyautogui
except Exception:
    pyautogui = None


class LaptopTools:

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(self):
        self.last_opened_app = None

    # =========================================================
    # BASIC GUI CHECK
    # =========================================================

    def _require_gui(self):
        if pyautogui is None:
            raise RuntimeError(
                "pyautogui is not installed. Run: pip install pyautogui"
            )

    # =========================================================
    # WINDOWS API HELPERS
    # =========================================================

    def _windows_available(self):
        return os.name == "nt"

    def _get_window_title(self, hwnd):
        try:
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)

            if length <= 0:
                return ""

            buffer = ctypes.create_unicode_buffer(length + 1)

            ctypes.windll.user32.GetWindowTextW(
                hwnd,
                buffer,
                length + 1
            )

            return buffer.value.strip()

        except Exception:
            return ""

    def _is_window_visible(self, hwnd):
        try:
            return bool(
                ctypes.windll.user32.IsWindowVisible(hwnd)
            )
        except Exception:
            return False

    def _activate_window(self, hwnd):
        try:
            user32 = ctypes.windll.user32

            # Restore if minimized.
            SW_RESTORE = 9

            user32.ShowWindow(hwnd, SW_RESTORE)

            # Bring the window to the foreground.
            user32.SetForegroundWindow(hwnd)

            # Additional foreground attempt.
            try:
                user32.BringWindowToTop(hwnd)
            except Exception:
                pass

            return True

        except Exception:
            return False

    def _find_window_by_keywords(self, keywords):
        """
        Find a visible top-level window whose title contains
        one of the supplied keywords.
        """

        if not self._windows_available():
            return None

        if isinstance(keywords, str):
            keywords = [keywords]

        normalized = [
            str(x).strip().casefold()
            for x in keywords
            if str(x).strip()
        ]

        if not normalized:
            return None

        found = []

        EnumWindowsProc = ctypes.WINFUNCTYPE(
            ctypes.c_bool,
            ctypes.c_void_p,
            ctypes.c_void_p
        )

        def callback(hwnd, lparam):

            try:
                if not self._is_window_visible(hwnd):
                    return True

                title = self._get_window_title(hwnd)

                if not title:
                    return True

                title_lower = title.casefold()

                for keyword in normalized:

                    if keyword in title_lower:
                        found.append(hwnd)
                        return False

            except Exception:
                pass

            return True

        try:
            ctypes.windll.user32.EnumWindows(
                EnumWindowsProc(callback),
                0
            )
        except Exception:
            return None

        return found[0] if found else None

    def _focus_app(self, app, timeout=8.0):
        """
        Wait for and activate the application window.

        This is critical for reliable multi-step commands such as:

            Open Notepad and type Hello
        """

        if not self._windows_available():
            return False

        app = str(app).strip().casefold()

        window_keywords = {

            "notepad": [
                "notepad",
            ],

            "calculator": [
                "calculator",
            ],

            "calc": [
                "calculator",
            ],

            "vscode": [
                "visual studio code",
                "vs code",
            ],

            "explorer": [
                "file explorer",
                "explorer",
            ],

            "file explorer": [
                "file explorer",
                "explorer",
            ],

            "paint": [
                "paint",
            ],

            "wordpad": [
                "wordpad",
            ],

            "powershell": [
                "powershell",
            ],

            "cmd": [
                "command prompt",
                "cmd",
            ],

            "terminal": [
                "terminal",
                "windows terminal",
            ],

            "chrome": [
                "google chrome",
            ],

            "edge": [
                "microsoft edge",
            ],

            "firefox": [
                "mozilla firefox",
                "firefox",
            ],

            "brave": [
                "brave",
            ],
        }

        keywords = window_keywords.get(
            app,
            [app]
        )

        deadline = time.time() + timeout

        while time.time() < deadline:

            hwnd = self._find_window_by_keywords(
                keywords
            )

            if hwnd:

                if self._activate_window(hwnd):

                    # Give Windows time to actually change focus.
                    time.sleep(0.35)

                    try:
                        foreground = ctypes.windll.user32.GetForegroundWindow()

                        if foreground == hwnd:
                            return True
                    except Exception:
                        # Even if foreground verification fails,
                        # the activation attempt succeeded.
                        return True

            time.sleep(0.25)

        return False

    # =========================================================
    # OPEN APPLICATION
    # =========================================================

    def open_app(self, app):

        access_controller.authorize(
            "app_launch",
            target=app
        )

        a = str(app).lower().strip()

        commands = {

            "chrome": [
                "cmd",
                "/c",
                "start",
                "",
                "chrome"
            ],

            "edge": [
                "cmd",
                "/c",
                "start",
                "",
                "msedge"
            ],

            "firefox": [
                "cmd",
                "/c",
                "start",
                "",
                "firefox"
            ],

            "brave": [
                "cmd",
                "/c",
                "start",
                "",
                "brave"
            ],

            "notepad": [
                "notepad.exe"
            ],

            "calculator": [
                "calc.exe"
            ],

            "calc": [
                "calc.exe"
            ],

            "vscode": [
                "cmd",
                "/c",
                "start",
                "",
                "code"
            ],

            "explorer": [
                "explorer.exe"
            ],

            "file explorer": [
                "explorer.exe"
            ],

            "paint": [
                "mspaint.exe"
            ],

            "wordpad": [
                "write.exe"
            ],

            "powershell": [
                "powershell.exe"
            ],

            "cmd": [
                "cmd.exe"
            ],

            "terminal": [
                "wt.exe"
            ],
        }

        if a not in commands:
            raise ValueError(
                f"Unsupported/blocked application: {app}"
            )

        print(
            f"🖥️ PAIOS launching application: {a}"
        )

        process = subprocess.Popen(
            commands[a],
            shell=False
        )

        self.last_opened_app = a

        # Give the operating system a moment to create
        # the application window.
        time.sleep(0.7)

        focused = self._focus_app(
            a,
            timeout=8.0
        )

        if not focused:
            print(
                f"⚠️ Application launched but "
                f"foreground window was not confirmed: {a}"
            )

            # Do not immediately claim that focus is guaranteed.
            # The process itself did launch, however.
            return {
                "status": "success",
                "action": "open_app",
                "application": a,
                "pid": process.pid,
                "focused": False,
                "message": (
                    f"{a} launched, but Windows foreground "
                    f"focus could not be confirmed."
                )
            }

        print(
            f"✅ Application opened and focused: {a}"
        )

        return {
            "status": "success",
            "action": "open_app",
            "application": a,
            "pid": process.pid,
            "focused": True,
            "message": (
                f"{a} launched and brought to the foreground."
            )
        }

    # =========================================================
    # HOTKEY
    # =========================================================

    def hotkey(self, *keys):

        access_controller.authorize(
            "keyboard"
        )

        self._require_gui()

        pyautogui.hotkey(*keys)

        return {
            "status": "success",
            "action": "hotkey",
            "keys": list(keys)
        }

    # =========================================================
    # PRESS KEY
    # =========================================================

    def press(self, key):

        access_controller.authorize(
            "keyboard"
        )

        self._require_gui()

        pyautogui.press(key)

        return {
            "status": "success",
            "action": "press",
            "key": key
        }

    # =========================================================
    # TYPE TEXT
    # =========================================================

    def type_text(self, text, interval=0.01):

        access_controller.authorize(
            "keyboard"
        )

        self._require_gui()

        if text is None:
            raise ValueError(
                "Text cannot be None."
            )

        text = str(text)

        if not text:
            raise ValueError(
                "Text cannot be empty."
            )

        # -----------------------------------------------------
        # Re-focus the application that PAIOS most recently
        # opened.
        # -----------------------------------------------------

        if self.last_opened_app:

            print(
                f"🎯 Re-focusing application: "
                f"{self.last_opened_app}"
            )

            self._focus_app(
                self.last_opened_app,
                timeout=5.0
            )

        # -----------------------------------------------------
        # Allow Windows to settle keyboard focus.
        # -----------------------------------------------------

        time.sleep(0.35)

        print(
            f"⌨️ PAIOS typing: {text}"
        )

        pyautogui.write(
            text,
            interval=interval
        )

        # Give the target application time to process
        # the keyboard events.
        time.sleep(0.20)

        return {
            "status": "success",
            "action": "type",
            "text": text,
            "length": len(text),
            "target_application": (
                self.last_opened_app
            )
        }

    # =========================================================
    # CLICK
    # =========================================================

    def click(
        self,
        x=None,
        y=None,
        button="left",
        clicks=1
    ):

        access_controller.authorize(
            "mouse"
        )

        self._require_gui()

        if x is None or y is None:

            pyautogui.click(
                button=button,
                clicks=clicks
            )

        else:

            pyautogui.click(
                int(x),
                int(y),
                button=button,
                clicks=clicks
            )

        return {
            "status": "success",
            "action": "click",
            "x": x,
            "y": y,
            "button": button,
            "clicks": clicks
        }

    # =========================================================
    # MOVE MOUSE
    # =========================================================

    def move(
        self,
        x,
        y,
        duration=0.15
    ):

        access_controller.authorize(
            "mouse"
        )

        self._require_gui()

        pyautogui.moveTo(
            int(x),
            int(y),
            duration=duration
        )

        return {
            "status": "success",
            "action": "move",
            "x": x,
            "y": y
        }

    # =========================================================
    # SCROLL
    # =========================================================

    def scroll(self, amount):

        access_controller.authorize(
            "mouse"
        )

        self._require_gui()

        pyautogui.scroll(
            int(amount)
        )

        return {
            "status": "success",
            "action": "scroll",
            "amount": amount
        }

    # =========================================================
    # SCREENSHOT
    # =========================================================

    def screenshot(self, path=None):

        access_controller.authorize(
            "screenshot"
        )

        self._require_gui()

        if path:

            access_controller.authorize(
                "filesystem_write",
                target=path
            )

            p = access_controller.safe_path(
                path
            )

            p.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            pyautogui.screenshot(
                str(p)
            )

            return {
                "status": "success",
                "path": str(p)
            }

        img = pyautogui.screenshot()

        return {
            "status": "success",
            "image": img
        }

    # =========================================================
    # SCREEN SIZE
    # =========================================================

    def get_screen_size(self):

        self._require_gui()

        s = pyautogui.size()

        return {
            "width": s.width,
            "height": s.height
        }

    # =========================================================
    # ACTIVE WINDOW
    # =========================================================

    def active_window_hint(self):

        if not self._windows_available():

            return {
                "status": "success",
                "note": (
                    "Windows foreground-window "
                    "inspection is unavailable."
                )
            }

        try:

            hwnd = ctypes.windll.user32.GetForegroundWindow()

            title = self._get_window_title(
                hwnd
            )

            return {
                "status": "success",
                "title": title,
                "hwnd": int(hwnd)
            }

        except Exception as e:

            return {
                "status": "success",
                "title": "",
                "error": str(e)
            }

    # =========================================================
    # WAIT
    # =========================================================

    def wait(self, seconds):

        seconds = max(
            0,
            float(seconds)
        )

        time.sleep(seconds)

        return {
            "status": "success",
            "action": "wait",
            "seconds": seconds
        }

    # =========================================================
    # CLIPBOARD / EDITING
    # =========================================================

    def copy(self):
        return self.hotkey(
            "ctrl",
            "c"
        )

    def paste(self):
        return self.hotkey(
            "ctrl",
            "v"
        )

    def save(self):
        return self.hotkey(
            "ctrl",
            "s"
        )

    def undo(self):
        return self.hotkey(
            "ctrl",
            "z"
        )

    def redo(self):
        return self.hotkey(
            "ctrl",
            "y"
        )

    def select_all(self):
        return self.hotkey(
            "ctrl",
            "a"
        )

    # =========================================================
    # WINDOW CONTROL
    # =========================================================

    def close_window(self):
        return self.hotkey(
            "alt",
            "f4"
        )

    def minimize_window(self):
        return self.hotkey(
            "win",
            "down"
        )

    def maximize_window(self):
        return self.hotkey(
            "win",
            "up"
        )

    def show_desktop(self):
        return self.hotkey(
            "win",
            "d"
        )

    # =========================================================
    # FILESYSTEM
    # =========================================================

    def read_text_file(self, path):

        access_controller.authorize(
            "filesystem_read",
            target=path
        )

        p = access_controller.safe_path(
            path
        )

        return {
            "status": "success",
            "path": str(p),
            "content": p.read_text(
                encoding="utf-8",
                errors="replace"
            )
        }

    def write_text_file(
        self,
        path,
        text
    ):

        access_controller.authorize(
            "filesystem_write",
            target=path
        )

        p = access_controller.safe_path(
            path
        )

        p.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        p.write_text(
            str(text),
            encoding="utf-8"
        )

        return {
            "status": "success",
            "path": str(p)
        }

    def list_dir(self, path=None):

        p = access_controller.safe_path(
            path or Path.home()
        )

        access_controller.authorize(
            "filesystem_read",
            target=p
        )

        return {
            "status": "success",
            "path": str(p),
            "items": [
                x.name
                for x in p.iterdir()
            ]
        }

    def copy_file(
        self,
        src,
        dst
    ):

        access_controller.authorize(
            "filesystem_read",
            target=src
        )

        access_controller.authorize(
            "filesystem_write",
            target=dst
        )

        s = access_controller.safe_path(
            src
        )

        d = access_controller.safe_path(
            dst
        )

        d.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        shutil.copy2(
            s,
            d
        )

        return {
            "status": "success",
            "source": str(s),
            "destination": str(d)
        }


# =============================================================
# GLOBAL INSTANCE
# =============================================================

laptop_tools = LaptopTools()