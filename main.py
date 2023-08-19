import os
import firebase_admin
import requests
from firebase_admin import firestore
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from collections import defaultdict
from dotenv import load_dotenv
from spotify_watcher import SpotifyWatcher
from models.contact_form import ContactForm
from starlette.middleware.cors import CORSMiddleware
import json
load_dotenv()


# Initialize Firestore DB
cred = firebase_admin.credentials.Certificate(
    json.loads((os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")))
)
firebase_admin.initialize_app(cred)
db = firestore.client()

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")
discord_webhook = os.getenv("DISCORD_WEBHOOK")

sp = SpotifyWatcher(client_id=client_id, client_secret=client_secret, refresh_token=refresh_token)
app = FastAPI(docs_url=None, redoc_url=None)

# CORS (allows requests from any origin)
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def custom_form_validation_error(request, exc):
    reformatted_message = defaultdict(list)
    for pydantic_error in exc.errors():
        loc, msg = pydantic_error["loc"], pydantic_error["msg"].capitalize()
        filtered_loc = loc[1:] if loc[0] in ("body", "query", "path") else loc
        field_string = ".".join(filtered_loc)
        reformatted_message[field_string].append(msg)

    return JSONResponse(
        status_code=400,
        content={
            "status": "error",
            "message": "Invalid request",
            "errors": reformatted_message,
        }
    )


@app.get('/')
def home():
    return JSONResponse(
        status_code=200,
        content={
            'status': 'ok',
            'message': 'aduq.dev backend is up and running.',
        }
    )


@app.get('/currently-playing')
async def currently_playing():
    return sp.get_currently_playing()


@app.post('/contact')
async def contact(contactForm: ContactForm, request: Request):
    # Send discord message through webhook
    data = {
        "content": "<@150541123851386880> A contact form has just been submitted:\n" +
        f"**FROM:** {contactForm.email}\n" +
        f"**SUBJECT:** {contactForm.subject}\n" +
        f"**MESSAGE:** {contactForm.message}",
        "embeds": None,
        "attachments": []
    }
    requests.post(discord_webhook, data=data)
    try:
        update_time, ref = db.collection('submitted-contact-forms').add({
            'email': contactForm.email,
            'subject': contactForm.subject,
            'message': contactForm.message,
            'date': firestore.SERVER_TIMESTAMP,
            'ip': request.client.host
        })
        return JSONResponse(
            status_code=200,
            content={
                'status': 'ok',
                'message': f'Message sent successfully at {update_time}. Ref ID: {ref.id}',
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                'status': 'error',
                'message': f'Error sending message: {e}',
            }
        )
