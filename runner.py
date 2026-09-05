from __future__ import annotations
import argparse, logging, os, sys
from app.config import load_people
from app.http import HttpClient
from app.pipeline import Pipeline
from sources.youtube import YouTubeClient
from sources.spotify import SpotifyClient
from delivery.telegram import TelegramClient
from storage.state import StateStore
from monitoring.health import HealthStore


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--mode',choices=['production','debug'],default='production'); args=ap.parse_args()
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    required=['YOUTUBE_API_KEY','TELEGRAM_BOT_TOKEN','TELEGRAM_CHAT_ID','TELEGRAM_HEALTH_CHAT_ID']
    missing=[x for x in required if not os.getenv(x)]
    if missing: raise SystemExit('Missing required env: '+', '.join(missing))
    http=HttpClient(); yt=YouTubeClient(os.environ['YOUTUBE_API_KEY'],http)
    sp=None
    if os.getenv('SPOTIFY_CLIENT_ID') and os.getenv('SPOTIFY_CLIENT_SECRET'):
        sp=SpotifyClient(os.environ['SPOTIFY_CLIENT_ID'],os.environ['SPOTIFY_CLIENT_SECRET'],http)
    media_tg=TelegramClient(os.environ['TELEGRAM_BOT_TOKEN'],os.environ['TELEGRAM_CHAT_ID'],http)
    health_tg=TelegramClient(os.environ['TELEGRAM_BOT_TOKEN'],os.environ['TELEGRAM_HEALTH_CHAT_ID'],http)
    return Pipeline(load_people(),yt,sp,media_tg,health_tg,StateStore(),HealthStore(),dry_run=args.mode=='debug').run()

if __name__=='__main__': sys.exit(main())
