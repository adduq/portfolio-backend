import os
from fastapi import FastAPI
from dotenv import load_dotenv
from spotify_watcher import SpotifyWatcher
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")

sp = SpotifyWatcher(client_id=client_id, client_secret=client_secret, refresh_token=refresh_token)
app = FastAPI()

# CORS (allows requests from any origin)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def home():
    return "Home"


@app.get('/currently-playing')
async def currently_playing():
    return sp.get_currently_playing()
