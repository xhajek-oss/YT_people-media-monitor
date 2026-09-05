from __future__ import annotations
from datetime import datetime, timezone, timedelta
import logging
from matching.identity import evaluate_identity
from matching.spotify import best_match

log=logging.getLogger(__name__)

class Pipeline:
    def __init__(self, people, youtube, spotify, telegram, state, health, dry_run=False):
        self.people=people; self.youtube=youtube; self.spotify=spotify; self.telegram=telegram; self.state=state; self.health=health; self.dry_run=dry_run

    def run(self):
        now=datetime.now(timezone.utc); collected={}; searched_ok=set()
        for p in self.people:
            ps=self.state.person(p.id); last=ps.get('last_successful_search_at'); initialized=bool(ps.get('initialized'))
            published_after=(datetime.fromisoformat(last.replace('Z','+00:00'))-timedelta(hours=4)) if last else (now-timedelta(hours=48))
            raw=[]
            try:
                for q in p.queries[:1]: raw.extend(self.youtube.search(q,published_after))
                self.health.person(p.id,'healthy',raw_results=len(raw),last_search_at=now.isoformat())
            except Exception as e:
                log.exception('YouTube search failed for %s',p.id); self.health.person(p.id,'down',error=str(e)); self.health.service('youtube','down',str(e)); continue
            for v in raw:
                if v.channel_id in p.exclude_channel_ids: continue
                ident=evaluate_identity(p,v)
                if ident.decision!='confirmed':
                    continue
                existing=self.state.item(v.video_id)
                if existing and existing.get('status') in {'delivered','baseline','rejected'}: continue
                item=collected.setdefault(v.video_id,{'video':v,'people':[],'initialized_flags':[]})
                if p.id not in item['people']: item['people'].append(p.id); v.matched_people.append(p.id); item['initialized_flags'].append(initialized)
            ps['last_successful_search_at']=now.isoformat(); searched_ok.add(p.id)
        candidates=[x['video'] for x in collected.values()]
        try:
            self.youtube.add_durations(candidates)
            if 'youtube' not in self.health.current['services']:
                self.health.service('youtube','healthy')
        except Exception as e:
            self.health.service('youtube','down',f'video details: {e}')
            self.state.save(); self.health.service('state','healthy'); self.health.finalize(); self.health.save()
            return 1

        by_id={p.id:p for p in self.people}
        for vid,bundle in collected.items():
            v=bundle['video']; p=by_id[bundle['people'][0]]
            if v.duration_seconds is None or v.duration_seconds < p.min_duration_seconds:
                self.state.put_item(vid,{'status':'rejected','reason':'too_short','duration_seconds':v.duration_seconds,'first_seen_at':now.isoformat(),'person_ids':bundle['people']}); continue
            if not all(bundle['initialized_flags']):
                self.state.put_item(vid,{'status':'baseline','first_seen_at':now.isoformat(),'person_ids':bundle['people'],'youtube_url':v.youtube_url}); continue
            selected_url=v.youtube_url; selected='youtube'; sp=None
            if p.spotify_enabled and self.spotify:
                try:
                    episodes=[]
                    for q in (v.title, f'{v.title} {p.name}'):
                        episodes.extend(self.spotify.search_episodes(q))
                    uniq={e['id']:e for e in episodes if e and e.get('id')}
                    sp=best_match(v,p,list(uniq.values()))
                    if sp: selected_url=sp.url; selected='spotify'
                    self.health.service('spotify','healthy')
                except Exception as e:
                    self.health.service('spotify','warning',str(e)); log.exception('Spotify lookup failed')
            elif 'spotify' not in self.health.current['services']:
                self.health.service('spotify','unchecked')
            names=', '.join(by_id[x].name for x in bundle['people'])
            text=f'🎙 {names}\n\n{v.title}\nKanál: {v.channel_title}\n\n{selected_url}'
            payload={'status':'delivery_pending','first_seen_at':now.isoformat(),'person_ids':bundle['people'],'youtube_url':v.youtube_url,'selected_source':selected,'selected_url':selected_url,'duration_seconds':v.duration_seconds}
            if sp: payload['spotify_episode_id']=sp.episode_id; payload['spotify_score']=round(sp.score,3)
            self.state.put_item(vid,payload); self.state.save()
            try:
                if not self.dry_run: self.telegram.send(text)
                payload['status']='delivered' if not self.dry_run else 'dry_run'; payload['delivered_at']=datetime.now(timezone.utc).isoformat() if not self.dry_run else None
                self.health.service('telegram','healthy' if not self.dry_run else 'unchecked')
            except Exception as e:
                payload['status']='delivery_failed'; payload['last_error']=str(e); self.health.service('telegram','down',str(e)); log.exception('Telegram delivery failed')
            self.state.put_item(vid,payload); self.state.save()

        for p in self.people:
            if p.id in searched_ok:
                self.state.person(p.id)['initialized']=True
        if 'spotify' not in self.health.current['services']:
            self.health.service('spotify','unchecked')
        if 'telegram' not in self.health.current['services']:
            self.health.service('telegram','unchecked')
        self.state.prune(); self.state.save(); self.health.service('state','healthy'); self.health.finalize()
        transition=self.health.transition(); self.health.save()
        if transition and self.telegram and not self.dry_run:
            old,new=transition
            try:
                emoji='✅' if new=='healthy' else '⚠️'
                self.telegram.send(f'{emoji} Media monitor health: {old} → {new}')
            except Exception: log.exception('Health transition alert failed')
        return 1 if self.health.current['overall']=='down' else 0
