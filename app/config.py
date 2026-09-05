from __future__ import annotations
from pathlib import Path
import yaml
from app.models import IdentityConfig, PersonProfile


def load_people(path: str | Path = 'config/people.yaml') -> list[PersonProfile]:
    raw = yaml.safe_load(Path(path).read_text(encoding='utf-8')) or {}
    defaults = raw.get('defaults', {})
    out: list[PersonProfile] = []
    for item in raw.get('people', []):
        if not item.get('enabled', True):
            continue
        yt = item.get('youtube', {})
        ident = item.get('identity', {})
        out.append(PersonProfile(
            id=item['id'],
            name=item['name'],
            aliases=tuple(item.get('aliases') or [item['name']]),
            queries=tuple(yt.get('queries') or [item['name']]),
            exclude_channel_ids=frozenset(yt.get('exclude_channel_ids', [])),
            min_duration_seconds=int(yt.get('min_duration_seconds', defaults.get('min_duration_seconds', 300))),
            spotify_enabled=bool(item.get('spotify', {}).get('enabled', True)),
            identity=IdentityConfig(
                mode=ident.get('mode','normal'),
                positive_terms=tuple(ident.get('positive_terms', [])),
                negative_terms=tuple(ident.get('negative_terms', [])),
                min_score=int(ident.get('min_score', 3)),
                uncertain_min_score=int(ident.get('uncertain_min_score', 1)),
            ),
        ))
    return out
