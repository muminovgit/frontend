"""Eskiz.uz SMS client. DRY-RUN by default. Needs ESKIZ_EMAIL / ESKIZ_PASSWORD env vars."""
import json, os, time, urllib.parse, urllib.request

BASE = "https://notify.eskiz.uz/api"

class Eskiz:
    def __init__(self, sender="4546", dry_run=True):
        self.sender, self.dry_run, self.token = sender, dry_run, None

    def _call(self, path, data=None, auth=True):
        body = urllib.parse.urlencode(data).encode() if data is not None else None
        req = urllib.request.Request(BASE + path, data=body)
        if auth:
            req.add_header("Authorization", f"Bearer {self.token}")
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)

    def login(self):
        r = self._call("/auth/login", {"email": os.environ["ESKIZ_EMAIL"], "password": os.environ["ESKIZ_PASSWORD"]}, auth=False)
        self.token = r["data"]["token"]

    def send(self, phone, text):
        if self.dry_run:
            return {"dry_run": True, "to": phone, "text": text}
        if not self.token: self.login()
        return self._call("/message/sms/send", {"mobile_phone": phone, "message": text, "from": self.sender})

    def send_many(self, items, delay=0.3):
        out = []
        for phone, text in items:
            out.append(self.send(phone, text)); time.sleep(0 if self.dry_run else delay)
        return out
