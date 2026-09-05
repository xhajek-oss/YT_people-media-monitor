from __future__ import annotations
from app.http import HttpClient

class TelegramClient:
    def __init__(self, token: str, chat_id: str, http: HttpClient): self.token=token; self.chat_id=chat_id; self.http=http
    def send(self, text: str) -> None:
        self.http.request('POST',f'https://api.telegram.org/bot{self.token}/sendMessage',json={'chat_id':self.chat_id,'text':text,'disable_web_page_preview':False})
