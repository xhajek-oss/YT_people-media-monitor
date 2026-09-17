# People Media Monitor

Hourly GitHub Actions monitor for appearances of configured people on YouTube channels other than their own. New long-form videos are identity-checked, matched to Spotify when a confident equivalent episode exists, and then delivered to Telegram. YouTube is the discovery source; Spotify is enrichment only.

## Pipeline

YouTube search → excluded-channel filter → identity verification → dedupe → 5-minute minimum → Spotify match → Telegram → delivered state.

The first successful run for each person establishes a 48-hour baseline and sends nothing. State is only marked `delivered` after a successful Telegram call; delivery failures remain retryable.

## YouTube channel exclusions

Excluded channels can be configured either by exact `UC...` channel ID or, preferably, by the channel `@handle` copied directly from its YouTube URL:

```yaml
youtube:
  exclude_channel_ids: []
  exclude_channel_handles: ["@example_channel"]
```

Do not guess a `UC...` ID when a usable handle is available. The monitor resolves every configured `@handle` through the YouTube Data API `channels.list(forHandle=...)` before filtering search results, using the existing `YOUTUBE_API_KEY`. Resolved handles are cached for the duration of each run.

When the user provides a channel URL such as `https://youtube.com/@example_channel?si=...`, store `@example_channel` in `exclude_channel_handles`. This mirrors the handle-resolution approach used by `YT-playlist-Formuler` and avoids incorrect manually inferred channel IDs.

## Secrets

Configure GitHub Actions secrets: `YOUTUBE_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`.

## Local debug

```bash
pip install -r requirements.txt
python runner.py --mode debug
python -m pytest -q
```

Edit `config/people.yaml` to add people, aliases, excluded channel IDs/handles, identity context, and minimum duration.
