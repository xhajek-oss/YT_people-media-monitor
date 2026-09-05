from __future__ import annotations
from datetime import datetime
from app.http import HttpClient
from app.models import VideoCandidate

class YouTubeClient:
    SEARCH='https://www.googleapis.com/youtube/v3/search'
    VIDEOS='https://www.googleapis.com/youtube/v3/videos'
    def __init__(self, api_key: str, http: HttpClient):
        self.api_key=api_key; self.http=http

    def search(self, query: str, published_after: datetime, max_results: int = 20) -> list[VideoCandidate]:
        params={'part':'snippet','type':'video','order':'date','q':query,'publishedAfter':published_after.isoformat().replace('+00:00','Z'),'maxResults':max_results,'key':self.api_key}
        data=self.http.request('GET',self.SEARCH,params=params).json()
        out=[]
        for it in data.get('items',[]):
            sn=it['snippet']; vid=it['id']['videoId']
            out.append(VideoCandidate(vid,sn.get('title',''),sn.get('description',''),sn.get('channelId',''),sn.get('channelTitle',''),datetime.fromisoformat(sn['publishedAt'].replace('Z','+00:00'))))
        return out

    def add_durations(self, videos: list[VideoCandidate]) -> None:
        ids=[v.video_id for v in videos]
        for i in range(0,len(ids),50):
            batch=ids[i:i+50]
            data=self.http.request('GET',self.VIDEOS,params={'part':'contentDetails,status','id':','.join(batch),'key':self.api_key}).json()
            by_id={x['id']:x for x in data.get('items',[])}
            for v in videos:
                item=by_id.get(v.video_id)
                if item:
                    v.duration_seconds=parse_duration(item['contentDetails'].get('duration','PT0S'))

def parse_duration(value: str) -> int:
    import re
    m=re.fullmatch(r'P(?:(\d+)D)?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?',value)
    if not m: return 0
    d,h,mn,s=(int(x or 0) for x in m.groups())
    return d*86400+h*3600+mn*60+s
