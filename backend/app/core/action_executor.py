from app.tools.browser_tools import browser_tools
from app.tools.laptop_tools import laptop_tools
import time
class ActionExecutor:
    def __init__(self): pass
    def _set_state(self,state,attribute,value):
        if state is None:return
        try:
            fn=getattr(state,'set_'+attribute,None)
            if callable(fn): fn(value); return
        except Exception: pass
        try:setattr(state,attribute,value)
        except Exception:pass
    def _success(self,a,r): return {'status':'success','action':a,'result':r}
    def _failure(self,a,e,recoverable=True): return {'status':'failed','action':a,'error':str(e),'recoverable':recoverable}
    def execute_action(self,action,state=None,step_number=1):
        if not isinstance(action,dict): return self._failure('unknown','Action must be a dictionary.',False)
        a=str(action.get('action','')).lower().strip(); self._set_state(state,'status','executing'); start=time.time()
        try:
            if a=='search': r=browser_tools.search(action['query'])
            elif a=='open_url': r=browser_tools.open_url(action['url'])
            elif a=='click': r=browser_tools.click(action['target'])
            elif a=='fill': r=browser_tools.fill_from_command(action['target'],action['text'])
            elif a=='press': r=browser_tools.press_key(action['key'])
            elif a=='read': r=browser_tools.read_page()
            elif a=='find': r=browser_tools.find(action['target'])
            elif a=='hover': r=browser_tools.hover(action['target'])
            elif a=='select': r=browser_tools.select(action['target'],action['value'])
            elif a=='check': r=browser_tools.check(action['target'])
            elif a=='uncheck': r=browser_tools.uncheck(action['target'])
            elif a=='scroll': r=browser_tools.scroll(action.get('amount',700))
            elif a=='wait': r=browser_tools.wait(action.get('seconds',1))
            elif a=='back': r=browser_tools.back()
            elif a=='forward': r=browser_tools.forward()
            elif a=='reload': r=browser_tools.reload()
            elif a=='new_tab': r=browser_tools.new_tab(action.get('url'))
            elif a=='close_tab': r=browser_tools.close_tab()
            elif a=='tabs': r=browser_tools.tabs()
            elif a=='switch_tab': r=browser_tools.switch_tab(action['index'])
            elif a=='screenshot': r=browser_tools.screenshot(action.get('path'))
            elif a=='laptop_open_app': r=laptop_tools.open_app(action['app'])
            elif a=='laptop_click': r=laptop_tools.click(action.get('x'),action.get('y'),action.get('button','left'),action.get('clicks',1))
            elif a=='laptop_move': r=laptop_tools.move(action['x'],action['y'])
            elif a=='laptop_type': r=laptop_tools.type_text(action['text'])
            elif a=='laptop_press': r=laptop_tools.press(action['key'])
            elif a=='laptop_scroll': r=laptop_tools.scroll(action['amount'])
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
            else: return self._failure(a,f'Unsupported action: {a}',False)
            self._set_state(state,'status','completed'); return self._success(a,r)
        except Exception as e:
            self._set_state(state,'status','failed'); return self._failure(a,e,True)
    def execute(self,actions,state=None):
        if isinstance(actions,dict): actions=[actions]
        results=[]
        for i,a in enumerate(actions or [],1):
            r=self.execute_action(a,state,i); results.append(r)
            if r.get('status')!='success': return {'status':'failed','steps':results,'failed_step':i}
        return {'status':'success','steps':results,'completed':len(results)}
action_executor=ActionExecutor()
