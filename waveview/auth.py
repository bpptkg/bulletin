import json

import requests

from .config import BASE_DIR, conf


class JwtAuthentication:
    def __init__(self) -> None:
        self.token_file = BASE_DIR / "waveview-token.json"
        if not self.token_file.exists():
            self.save_token({})

    def save_token(self, token) -> None:
        with open(self.token_file, "w") as f:
            json.dump(token, f)

    def read_token(self) -> dict:
        with open(self.token_file, "r") as f:
            return json.load(f)

    def is_token_valid(self, access_token: str) -> bool:
        response = requests.get(
            conf.get_account_url,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        return response.ok

    def refresh_token(self, refresh_token: str) -> str:
        response = requests.post(
            conf.refresh_url,
            data={"refresh": refresh_token},
        )
        response.raise_for_status()
        new_token = response.json()
        token = self.read_token()
        token["access"] = new_token["access"]
        self.save_token(token)
        return token["access"]

    def authenticate(self) -> str:
        if not conf.enable_sync:
            return ""
        if not conf.username or not conf.password:
            raise ValueError("Username and password are required.")

        token = self.read_token()
        access_token = token.get("access")
        refresh_token = token.get("refresh")
        if access_token and self.is_token_valid(access_token):
            return access_token

        try:
            access_token = self.refresh_token(refresh_token)
            return access_token
        except requests.HTTPError:
            pass

        token = requests.post(
            conf.login_url,
            data={"username": conf.username, "password": conf.password},
        ).json()
        self.save_token(token)
        return token["access"]
