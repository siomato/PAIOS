"""Single-thread-owned Playwright browser with broad action coverage."""
from __future__ import annotations
import re, time
from urllib.parse import quote_plus, urlparse
from pathlib import Path
from app.tools.browser_worker import browser_worker
from app.security.access_control import access_controller
try: from playwright.sync_api import sync_playwright
except Exception: sync_playwright=None

class BrowserAutomation:
    def __init__(self): self.pw=None; self.browser=None; self.context=None; self.page=None; self.search_results=[]; self.last_search_query=''; self.last_search_engine=''
    def start(self):
        if self.page and not self.page.is_closed(): return self.page
        if sync_playwright is None: raise RuntimeError('playwright is not installed')
        self.pw=sync_playwright().start(); self.browser=self.pw.chromium.launch(headless=False); self.context=self.browser.new_context(accept_downloads=True,viewport={'width':1440,'height':900}); self.page=self.context.new_page(); return self.page
    def _telemetry(self):
        p=self.start(); return {'current_url':p.url,'page_title':p.title() if not p.is_closed() else None}
    def open_url(self,url):
        url=str(url).strip();
        if not re.match(r'^https?://',url,re.I): url='https://'+url
        access_controller.authorize_url(url); p=self.start(); p.goto(url,wait_until='domcontentloaded',timeout=30000); return {'status':'success','url':p.url,'title':p.title()}
    def search(self,query,engine='auto'):
        q=str(query).strip();
        if not q: raise ValueError('Search query cannot be empty')
        p=self.start(); engines=['google','bing','duckduckgo'] if engine=='auto' else [engine]
        last=None
        for e in engines:
            try:
                base={'google':'https://www.google.com/search?q=','bing':'https://www.bing.com/search?q=','duckduckgo':'https://duckduckgo.com/?q='}[e]
                p.goto(base+quote_plus(q),wait_until='domcontentloaded',timeout=20000); self.search_results=self._extract_results(); self.last_search_query=q; self.last_search_engine=e
                if self.search_results: return {'status':'success','engine':e,'query':q,'results':self.search_results,'url':p.url,'title':p.title()}
            except Exception as ex: last=ex
        raise RuntimeError(f'No usable search results: {last}')
    def google_search(self,q): return self.search(q,'google')
    def duckduckgo_search(self,q): return self.search(q,'duckduckgo')
    def _extract_results(self):
        p=self.start(); out=[]; seen=set()
        for a in p.locator('a').all():
            try:
                href=a.get_attribute('href') or ''; text=(a.inner_text() or '').strip()
                if not href or not text or len(text)<2: continue
                if href.startswith('/url?q='): href=href.split('/url?q=',1)[1].split('&',1)[0]
                if not re.match(r'^https?://',href): continue
                host=urlparse(href).netloc.lower()
                if any(x in host for x in ('google.com','bing.com','duckduckgo.com')): continue
                key=(text,href)
                if key in seen: continue
                seen.add(key); out.append({'title':text[:240],'url':href})
                if len(out)>=20: break
            except Exception: pass
        return out
    def get_search_results(self): return list(self.search_results)
    def get_first_search_result(self): return self.search_results[0] if self.search_results else None
    def get_last_search_result(self): return self.search_results[-1] if self.search_results else None
    def click(self,target):
        p=self.start(); t=str(target).strip()
        if t.lower() in ('first search result','first result','the first result') and self.search_results: return self.open_url(self.search_results[0]['url'])
        loc=self._resolve(t); loc.first.click(timeout=15000); return {'status':'success','action':'click','target':t,'url':p.url,'title':p.title()}
    def _resolve(self,t):
        p=self.start(); esc=re.escape(t)
        for sel in [f'get_by_role("button", name=re.compile("^{esc}$", re.I))',f'get_by_role("link", name=re.compile("{esc}", re.I))',f'get_by_text(re.compile("{esc}", re.I))',f'input[placeholder*="{t}"]',f'input[aria-label*="{t}"]']:
            try:
                # evaluate selectors safely through direct locator APIs
                if sel.startswith('get_by_role("button"'): l=p.get_by_role('button',name=re.compile(t,re.I))
                elif sel.startswith('get_by_role("link"'): l=p.get_by_role('link',name=re.compile(t,re.I))
                elif sel.startswith('get_by_text'): l=p.get_by_text(re.compile(t,re.I))
                elif 'placeholder' in sel: l=p.locator(f'input[placeholder*="{t}"]')
                else: l=p.locator(f'input[aria-label*="{t}"]')
                if l.count(): return l
            except Exception: pass
        raise ValueError(f'Could not resolve browser target: {t}')
    def fill(self,target,text):
        p=self.start(); t=str(target).strip(); value=str(text); l=self._resolve(t); l.first.fill(value); return {'status':'success','action':'fill','target':t,'url':p.url}
    def fill_from_command(self,target,text): return self.fill(target,text)
    def press_key(self,key): p=self.start(); p.keyboard.press(str(key)); return {'status':'success','action':'press','key':key,'url':p.url}
    def press(self,key): return self.press_key(key)
    def hover(self,target): self._resolve(target).first.hover(); return {'status':'success','action':'hover','target':target}
    def select(self,target,value): self._resolve(target).first.select_option(label=str(value)); return {'status':'success','action':'select','target':target,'value':value}
    def check(self,target): self._resolve(target).first.check(); return {'status':'success','action':'check','target':target}
    def uncheck(self,target): self._resolve(target).first.uncheck(); return {'status':'success','action':'uncheck','target':target}
    def scroll(self,amount=700): self.start().mouse.wheel(0,float(amount)); return {'status':'success','action':'scroll','amount':amount}
    def wait(self,seconds=1): time.sleep(max(0,float(seconds))); return {'status':'success','action':'wait','seconds':seconds}
    def back(self): p=self.start(); p.go_back(wait_until='domcontentloaded',timeout=20000); return self._telemetry()
    def forward(self): p=self.start(); p.go_forward(wait_until='domcontentloaded',timeout=20000); return self._telemetry()
    def reload(self): p=self.start(); p.reload(wait_until='domcontentloaded',timeout=20000); return self._telemetry()
    def new_tab(self,url=None): p=self.context.new_page(); self.page=p; return self.open_url(url) if url else {'status':'success','action':'new_tab','url':p.url}
    def close_tab(self):
        p=self.start(); p.close(); pages=[x for x in self.context.pages if not x.is_closed()]; self.page=pages[-1] if pages else self.context.new_page(); return self._telemetry()
    def tabs(self): return [{'index':i,'url':p.url,'title':p.title() if not p.is_closed() else ''} for i,p in enumerate(self.context.pages)]
    def switch_tab(self,index): pages=self.context.pages; i=int(index); self.page=pages[i]; return self._telemetry()
    def screenshot(self,path=None,full_page=True):
        p=self.start(); dest=path or str(Path.home()/'Downloads'/'paios_browser.png'); access_controller.authorize('filesystem_write',target=dest); p.screenshot(path=dest,full_page=full_page); return {'status':'success','path':dest}
    def read_page(self):
        p=self.start(); text=p.locator('body').inner_text(timeout=15000); return {'status':'success','url':p.url,'title':p.title(),'content':text[:30000]}
    def find(self,target):
        p=self.start(); l=self._resolve(target); return {'status':'success','target':target,'count':l.count()}
    def get_current_url(self): return self.start().url
    def get_page(self): return self.start()
    def get_page_title(self): return self.start().title()
    def open_youtube(self): return self.open_url('https://www.youtube.com')
    def open_chatgpt(self): return self.open_url('https://chatgpt.com')
    def open_github(self): return self.open_url('https://github.com')
    def open_linkedin(self): return self.open_url('https://www.linkedin.com')
    def open_gmail(self): return self.open_url('https://mail.google.com')
    def close(self):
        for x in (self.page,self.context,self.browser):
            try:
                if x: x.close()
            except Exception: pass
        try:
            if self.pw: self.pw.stop()
        except Exception: pass
        self.page=self.context=self.browser=self.pw=None
        return {'status':'success','message':'Browser closed'}
browser_automation=BrowserAutomation()
