from __future__ import annotations
from datetime import date
from difflib import SequenceMatcher
from app.models import SpotifyMatch, VideoCandidate, PersonProfile
from matching.identity import norm


def score_episode(video: VideoCandidate, person: PersonProfile, ep: dict) -> float:
    name=ep.get('name',''); show=(ep.get('show') or {}).get('name','')
    title_score=SequenceMatcher(None,norm(video.title),norm(name)).ratio()
    hay=norm(name+' '+show)
    person_ok=any(norm(a) in hay for a in person.aliases)
    if not person_ok: return 0.0
    date_score=0.0
    try:
        d=date.fromisoformat(ep.get('release_date',''))
        diff=abs((video.published_at.date()-d).days)
        if diff<=1: date_score=1
        elif diff<=3: date_score=.9
        elif diff<=7: date_score=.8
        elif diff<=14: date_score=.65
        else: return 0.0
    except Exception:
        return 0.0
    return title_score*.75+date_score*.25


def best_match(video: VideoCandidate, person: PersonProfile, episodes: list[dict], threshold: float=.78) -> SpotifyMatch | None:
    ranked=[(score_episode(video,person,e),e) for e in episodes]
    ranked=[x for x in ranked if x[0]>=threshold]
    if not ranked: return None
    score,e=max(ranked,key=lambda x:x[0])
    return SpotifyMatch(e['id'],e.get('name',''),(e.get('show') or {}).get('name',''),(e.get('external_urls') or {}).get('spotify',''),e.get('release_date',''),score)
