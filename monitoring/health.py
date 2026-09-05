from __future__ import annotations
import json, os
from pathlib import Path
from datetime import datetime, timezone

class HealthStore:
    def __init__(self,path='data/health.json'):
        self.path=Path(path); self.previous=self._load(); self.current={'last_run_at':datetime.now(timezone.utc).isoformat(),'overall':'healthy','services':{},'people':{}}
    def _load(self):
        try: return json.loads(self.path.read_text(encoding='utf-8'))
        except Exception: return {}
    def service(self,name,status,message=''): self.current['services'][name]={'status':status,'message':message}
    def person(self,pid,status,**meta): self.current['people'][pid]={'status':status,**meta}
    def finalize(self):
        statuses=[x.get('status') for x in self.current['services'].values()]+[x.get('status') for x in self.current['people'].values()]
        self.current['overall']='down' if 'down' in statuses else ('warning' if 'warning' in statuses else 'healthy')
    def transition(self):
        prev=self.previous.get('overall'); cur=self.current.get('overall')
        if prev and prev!=cur: return (prev,cur)
        if not prev and cur!='healthy': return ('unknown',cur)
        return None
    def save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True); tmp=self.path.with_suffix('.tmp')
        tmp.write_text(json.dumps(self.current,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8'); os.replace(tmp,self.path)
