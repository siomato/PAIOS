from app.tools.browser_tools import browser_tools
from app.core.action_planner import action_planner
class BrowserEngine:
    def can_handle(self,m):
        s=str(m).lower(); keys=('search','google','youtube','github','chatgpt','linkedin','gmail','website','web','browser','open url','navigate','go to','click','fill','type in','read page','find','scroll','hover','reload','refresh','back','forward','tab','screenshot','checkbox','select')
        return any(k in s for k in keys)
    def execute(self,message):
        plan=action_planner.plan(message); results=[]
        for step in plan:
            a=step.get('action')
            if a=='search': r=browser_tools.search(step['query'])
            elif a=='open_url': r=browser_tools.open_url(step['url'])
            elif a=='click': r=browser_tools.click(step['target'])
            elif a=='fill': r=browser_tools.fill_from_command(step['target'],step['text'])
            elif a=='press': r=browser_tools.press_key(step['key'])
            elif a=='read': r=browser_tools.read_page()
            elif a=='find': r=browser_tools.find(step['target'])
            elif a=='hover': r=browser_tools.hover(step['target'])
            elif a=='select': r=browser_tools.select(step['target'],step['value'])
            elif a=='check': r=browser_tools.check(step['target'])
            elif a=='uncheck': r=browser_tools.uncheck(step['target'])
            elif a=='scroll': r=browser_tools.scroll(step.get('amount',700))
            elif a=='wait': r=browser_tools.wait(step.get('seconds',1))
            elif a=='back': r=browser_tools.back()
            elif a=='forward': r=browser_tools.forward()
            elif a=='reload': r=browser_tools.reload()
            elif a=='new_tab': r=browser_tools.new_tab(step.get('url'))
            elif a=='close_tab': r=browser_tools.close_tab()
            elif a=='tabs': r=browser_tools.tabs()
            elif a=='switch_tab': r=browser_tools.switch_tab(step['index'])
            elif a=='screenshot': r=browser_tools.screenshot()
            else: raise ValueError(f'Unsupported browser action: {a}')
            results.append({'action':a,'result':r})
        return {'status':'success','steps':results,'count':len(results)}
browser_engine=BrowserEngine()
