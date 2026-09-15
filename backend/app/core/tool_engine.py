from app.tools.application_tools import application_tools
from app.tools.laptop_tools import laptop_tools
from app.core.action_planner import action_planner
class ToolEngine:
    def can_handle(self,m): return self._is_laptop(str(m))
    def _is_laptop(self,m):
        s=m.lower(); return any(x in s for x in ('open chrome','open notepad','open calculator','open calc','open vscode','open vs code','open visual studio code','open edge','open firefox','open brave','open explorer','show desktop','copy','paste','save','undo','redo','select all','move mouse','click at','double click','right click','type ','write ','press ','scroll up','scroll down','screenshot','minimize window','maximize window','close window'))
    def execute(self,message_or_intent):
        text=message_or_intent if isinstance(message_or_intent,str) else ''
        plan=action_planner.plan(text); results=[]
        for s in plan:
            a=s['action']
            if a=='laptop_open_app': r=laptop_tools.open_app(s['app'])
            elif a=='laptop_click': r=laptop_tools.click(s.get('x'),s.get('y'),s.get('button','left'),s.get('clicks',1))
            elif a=='laptop_move': r=laptop_tools.move(s['x'],s['y'])
            elif a=='laptop_type': r=laptop_tools.type_text(s['text'])
            elif a=='laptop_press': r=laptop_tools.press(s['key'])
            elif a=='laptop_scroll': r=laptop_tools.scroll(s['amount'])
            elif a=='laptop_copy': r=laptop_tools.copy()
            elif a=='laptop_paste': r=laptop_tools.paste()
            elif a=='laptop_save': r=laptop_tools.save()
            elif a=='laptop_undo': r=laptop_tools.undo()
            elif a=='laptop_redo': r=laptop_tools.redo()
            elif a=='laptop_select_all': r=laptop_tools.select_all()
            elif a=='laptop_close': r=laptop_tools.close_window()
            elif a=='laptop_minimize': r=laptop_tools.minimize_window()
            elif a=='laptop_maximize': r=laptop_tools.maximize_window()
            elif a=='laptop_show_desktop': r=laptop_tools.show_desktop()
            else: continue
            results.append({'action':a,'result':r})
        if not results: return None
        return {'status':'success','steps':results,'count':len(results)}
tool_engine=ToolEngine()
