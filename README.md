# People Media Monitor

Hourly GitHub Actions monitor for appearances of configured people on YouTube channels other than their own. New long-form videos are identity-checked, matched to Spotify when a confident equivalent episode exists, and then delivered to Telegram. YouTube is the discovery source; Spotify is enrichment only.

## Pipeline

YouTube search → excluded-channel filter → identity verification → dedupe → 5-minute minimum → Spotify match → Telegram → delivered state.

The first successful run for each person establishes a 48-hour baseline and sends nothing. State is only marked `delivered` after a successful Telegram call; delivery failures remain retryable.

## Secrets

Configure GitHub Actions secrets: `YOUTUBE_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`.

## Local debug

```bash
pip install -r requirements.txt
python runner.py --mode debug
python -m pytest -q
```

Edit `config/people.yaml` to add people, aliases, own channel IDs, identity context, and minimum duration.
