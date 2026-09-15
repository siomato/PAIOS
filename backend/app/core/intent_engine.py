import re
class IntentEngine:
    def __init__(self):
        self.apps={'chrome':'chrome','google chrome':'chrome','edge':'edge','firefox':'firefox','brave':'brave','notepad':'notepad','calculator':'calculator','calc':'calculator','vscode':'vscode','vs code':'vscode','visual studio code':'vscode','explorer':'explorer','file explorer':'explorer','paint':'paint','powershell':'powershell','terminal':'terminal'}
    def detect_intent(self,message):
        m=str(message).strip(); low=m.lower()
        for alias,app in sorted(self.apps.items(),key=lambda x:-len(x[0])):
            if re.search(r'\b(?:open|launch|start|run)\s+(?:the\s+)?'+re.escape(alias)+r'\b',low): return {'intent':'LAPTOP_APP','target':app}
        if any(x in low for x in ('search ','google ','look up ','find online','web search')): return {'intent':'BROWSER_AUTOMATION','target':None}
        if any(x in low for x in ('browser','website','webpage','click ','fill ','hover ','reload','refresh','open http','go to ','navigate to ','read page','scroll','new tab','close tab')): return {'intent':'BROWSER_AUTOMATION','target':None}
        if any(x in low for x in ('mouse','keyboard','type ','press ','hotkey','screenshot','show desktop','copy','paste','minimize','maximize','close window')): return {'intent':'LAPTOP_AUTOMATION','target':None}
        return {'intent':'CHAT','target':None}
intent_engine=IntentEngine()
