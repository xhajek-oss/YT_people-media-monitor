from __future__ import annotations
import base64, time
from app.http import HttpClient

class SpotifyClient:
    TOKEN='https://accounts.spotify.com/api/token'; SEARCH='https://api.spotify.com/v1/search'
    def __init__(self, client_id: str, client_secret: str, http: HttpClient):
        self.client_id=client_id; self.client_secret=client_secret; self.http=http; self._token=None; self._expires=0
    def token(self) -> str:
        if self._token and time.time()<self._expires: return self._token
        basic=base64.b64encode(f'{self.client_id}:{self.client_secret}'.encode()).decode()
        data=self.http.request('POST',self.TOKEN,headers={'Authorization':f'Basic {basic}'},data={'grant_type':'client_credentials'}).json()
        self._token=data['access_token']; self._expires=time.time()+int(data.get('expires_in',3600))-60
        return self._token
    def search_episodes(self, query: str, limit: int=10) -> list[dict]:
        r=self.http.request('GET',self.SEARCH,headers={'Authorization':f'Bearer {self.token()}'},params={'q':query,'type':'episode','limit':limit,'market':'CZ'})
        return (r.json().get('episodes') or {}).get('items',[])
