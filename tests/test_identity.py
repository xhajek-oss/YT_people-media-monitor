from datetime import datetime, timezone
from app.models import PersonProfile, IdentityConfig, VideoCandidate
from matching.identity import evaluate_identity

def p():
    return PersonProfile('d','David Svoboda',('David Svoboda',),('David Svoboda',),frozenset(),IdentityConfig('strict',('ukrajina','historik'),('moderní pětiboj','olympiáda'),6,2))
def v(title,desc=''):
    return VideoCandidate('x',title,desc,'c','ch',datetime.now(timezone.utc))

def test_accepts_ukrainian_context(): assert evaluate_identity(p(),v('David Svoboda: Co čeká Ukrajinu')).decision=='confirmed'
def test_rejects_athlete(): assert evaluate_identity(p(),v('David Svoboda a moderní pětiboj')).decision=='rejected'
def test_uncertain_plain_name(): assert evaluate_identity(p(),v('Rozhovor s Davidem Svobodou')).decision=='uncertain'
