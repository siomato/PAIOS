import subprocess


class ApplicationTools:

    def open_chrome(self):

        try:

            subprocess.Popen("start chrome", shell=True)

            return "Opening Google Chrome."

        except Exception as e:

            return f"Failed to open Chrome: {e}"

    def open_notepad(self):

        try:

            subprocess.Popen("notepad")

            return "Opening Notepad."

        except Exception as e:

            return f"Failed to open Notepad: {e}"

    def open_calculator(self):

        try:

            subprocess.Popen("calc")

            return "Opening Calculator."

        except Exception as e:

            return f"Failed to open Calculator: {e}"

    def open_vscode(self):

        try:

            subprocess.Popen(
                r'"C:\Users\cyril\AppData\Local\Programs\Microsoft VS Code\Code.exe"',
                shell=True
            )

            return "Opening Visual Studio Code."

        except Exception as e:

            return f"Failed to open VS Code: {e}"


application_tools = ApplicationTools()