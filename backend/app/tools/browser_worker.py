import threading, queue, traceback
class BrowserWorker:
    def __init__(self):
        self._queue=queue.Queue(); self._thread=threading.Thread(target=self._run,daemon=True,name='PAIOS-BrowserWorker'); self._started=False; self._lock=threading.Lock()
    def start(self):
        with self._lock:
            if not self._started: self._started=True; self._thread.start(); print('🧵 PAIOS BrowserWorker started')
    def _run(self):
        while True:
            fn,args,kwargs,rq=self._queue.get()
            try: rq.put((True,fn(*args,**kwargs)))
            except Exception as e: traceback.print_exc(); rq.put((False,e))
            finally: self._queue.task_done()
    def execute(self,fn,*args,timeout=90,**kwargs):
        if threading.current_thread() is self._thread: return fn(*args,**kwargs)
        self.start(); rq=queue.Queue(maxsize=1); self._queue.put((fn,args,kwargs,rq)); ok,res=rq.get(timeout=timeout)
        if not ok: raise res
        return res
browser_worker=BrowserWorker()
