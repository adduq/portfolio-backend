import requests
import time
import base64


class SpotifyWatcher:
    def __init__(self, client_id, client_secret, refresh_token):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = None
        self.token_expires_at = None
        self.last_fetched_at = None
        self.current_track: dict = None

    def __get_access_token(self):
        if self.access_token is not None and self.token_expires_at is not None and time.time() < self.token_expires_at:
            return self.access_token

        url = "https://accounts.spotify.com/api/token"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        client_creds = f"{self.client_id}:{self.client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        headers = {"Authorization": f"Basic {client_creds_b64.decode()}"}
        response = requests.post(url, data=payload, headers=headers)
        data = response.json()
        self.token_expires_at = time.time() + data["expires_in"]
        self.access_token = data["access_token"]
        return self.access_token

    def get_currently_playing(self) -> dict:
        if self.last_fetched_at is not None and time.time() - self.last_fetched_at < 5:
            return self.current_track  # return cached track

        url = "https://api.spotify.com/v1/me/player/currently-playing"
        headers = {"Authorization": f"Bearer {self.__get_access_token()}"}
        response = requests.get(url, headers=headers)
        self.last_fetched_at = time.time()
        if response.status_code == 204:
            self.current_track = None
            return None

        data = response.json()
        track = {
            "name": data["item"]["name"],
            "artist": data["item"]["artists"][0]["name"],
            "image_url": data["item"]["album"]["images"][0]["url"],
            "track_url": data["item"]["external_urls"]["spotify"],
            "artist_url": data["item"]["artists"][0]["external_urls"]["spotify"],
            "preview_url": data["item"]["preview_url"],
            "duration_ms": data["item"]["duration_ms"],
            "progress_ms": data["progress_ms"],
        }
        self.current_track = track
        return track
