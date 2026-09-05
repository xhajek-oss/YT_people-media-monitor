from __future__ import annotations
import re, unicodedata
from app.models import IdentityMatch, PersonProfile, VideoCandidate


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", s)).strip()


def _token_match(needle: str, token: str) -> bool:
    if needle == token:
        return True
    if len(needle) >= 5 and len(token) >= 5:
        stem = min(6, len(needle), len(token))
        return needle[:stem] == token[:stem]
    return False


def phrase_match(phrase: str, text: str) -> bool:
    wanted = norm(phrase).split()
    tokens = norm(text).split()
    if not wanted:
        return False
    pos = 0
    for w in wanted:
        found = False
        while pos < len(tokens):
            if _token_match(w, tokens[pos]):
                found = True
                pos += 1
                break
            pos += 1
        if not found:
            return False
    return True


def evaluate_identity(person: PersonProfile, video: VideoCandidate) -> IdentityMatch:
    title, desc = video.title or "", video.description or ""
    alias_title = any(phrase_match(a, title) for a in person.aliases)
    alias_desc = any(phrase_match(a, desc) for a in person.aliases)
    reasons: list[str] = []
    score = 0

    if alias_title:
        score += 5
        reasons.append("alias in title +5")
    elif alias_desc:
        score += 2
        reasons.append("alias in description +2")
    else:
        return IdentityMatch("rejected", 0, ("no alias match",))

    for term in person.identity.negative_terms:
        if phrase_match(term, title):
            return IdentityMatch("rejected", -10, (f"negative title term: {term}",))
        if phrase_match(term, desc):
            score -= 5
            reasons.append(f"negative description term: {term} -5")

    positive = False
    for term in person.identity.positive_terms:
        if phrase_match(term, title):
            positive = True
            score += 3
            reasons.append(f"positive title term: {term} +3")
        elif phrase_match(term, desc):
            positive = True
            score += 1
            reasons.append(f"positive description term: {term} +1")

    if person.identity.mode == "strict" and not positive:
        return IdentityMatch("uncertain", score, tuple(reasons + ["strict profile needs positive context"]))
    if score >= person.identity.min_score:
        return IdentityMatch("confirmed", score, tuple(reasons))
    if score >= person.identity.uncertain_min_score:
        return IdentityMatch("uncertain", score, tuple(reasons))
    return IdentityMatch("rejected", score, tuple(reasons))
