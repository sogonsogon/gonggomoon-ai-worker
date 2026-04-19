import json
import urllib.request
from typing import Any

from app.application.ports.ports import CallbackPort


class HttpCallbackClient(CallbackPort):
    def send(self, callback_url: str, body: dict[str, Any]) -> None:
        print(f"log : starting to send callback to {callback_url}")

        payload = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            callback_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5):
            return
