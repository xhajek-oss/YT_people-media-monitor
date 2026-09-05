from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

HealthStatus = Literal['healthy','warning','down','unchecked']

@dataclass(frozen=True)
class IdentityConfig:
    mode: str = 'normal'
    positive_terms: tuple[str, ...] = ()
    negative_terms: tuple[str, ...] = ()
    min_score: int = 3
    uncertain_min_score: int = 1

@dataclass(frozen=True)
class PersonProfile:
    id: str
    name: str
    aliases: tuple[str, ...]
    queries: tuple[str, ...]
    exclude_channel_ids: frozenset[str]
    identity: IdentityConfig
    min_duration_seconds: int = 300
    spotify_enabled: bool = True

@dataclass
class VideoCandidate:
    video_id: str
    title: str
    description: str
    channel_id: str
    channel_title: str
    published_at: datetime
    duration_seconds: int | None = None
    matched_people: list[str] = field(default_factory=list)

    @property
    def youtube_url(self) -> str:
        return f'https://www.youtube.com/watch?v={self.video_id}'

@dataclass(frozen=True)
class IdentityMatch:
    decision: Literal['confirmed','uncertain','rejected']
    score: int
    reasons: tuple[str, ...]

@dataclass(frozen=True)
class SpotifyMatch:
    episode_id: str
    title: str
    show_name: str
    url: str
    release_date: str
    score: float
