from __future__ import annotations
import time
import requests

RETRYABLE = {429, 500, 502, 503, 504}

class HttpClient:
    def __init__(self, timeout: int = 20, attempts: int = 3):
        self.session = requests.Session()
        self.timeout = timeout
        self.attempts = attempts

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        last_exc = None
        for attempt in range(self.attempts):
            try:
                r = self.session.request(method, url, timeout=self.timeout, **kwargs)
                if r.status_code not in RETRYABLE:
                    r.raise_for_status()
                    return r
                if attempt == self.attempts - 1:
                    r.raise_for_status()
                retry_after = r.headers.get('Retry-After')
                delay = float(retry_after) if retry_after and retry_after.isdigit() else (1,3,8)[min(attempt,2)]
                time.sleep(delay)
            except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as exc:
                last_exc = exc
                if isinstance(exc, requests.HTTPError) and exc.response is not None and exc.response.status_code not in RETRYABLE:
                    raise
                if attempt == self.attempts - 1:
                    raise
                time.sleep((1,3,8)[min(attempt,2)])
        raise last_exc or RuntimeError('HTTP request failed')
