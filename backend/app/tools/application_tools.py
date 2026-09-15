from app.tools.laptop_tools import laptop_tools
class ApplicationTools:
    def open_chrome(self): return laptop_tools.open_app('chrome')
    def open_notepad(self): return laptop_tools.open_app('notepad')
    def open_calculator(self): return laptop_tools.open_app('calculator')
    def open_vscode(self): return laptop_tools.open_app('vscode')
    def open(self,name): return laptop_tools.open_app(name)
application_tools=ApplicationTools()
