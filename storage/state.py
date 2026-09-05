from __future__ import annotations
import json, os
from pathlib import Path
from datetime import datetime, timezone, timedelta

class StateStore:
    def __init__(self,path='data/state.json'):
        self.path=Path(path); self.data=self._load()
    def _load(self):
        if not self.path.exists(): return {'version':1,'people':{},'items':{}}
        return json.loads(self.path.read_text(encoding='utf-8'))
    def person(self,pid): return self.data.setdefault('people',{}).setdefault(pid,{})
    def item(self,vid): return self.data.setdefault('items',{}).get(f'youtube:{vid}')
    def put_item(self,vid,payload): self.data.setdefault('items',{})[f'youtube:{vid}']=payload
    def save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True); tmp=self.path.with_suffix('.tmp')
        tmp.write_text(json.dumps(self.data,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8'); os.replace(tmp,self.path)
    def prune(self,days=90):
        cutoff=datetime.now(timezone.utc)-timedelta(days=days); keep={}
        for k,v in self.data.get('items',{}).items():
            ts=v.get('delivered_at') or v.get('first_seen_at')
            try:
                if not ts or datetime.fromisoformat(ts.replace('Z','+00:00'))>=cutoff: keep[k]=v
            except Exception: keep[k]=v
        self.data['items']=keep
