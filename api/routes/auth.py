# FastAPI
from discord.ext import commands
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse

# Serialization
from itsdangerous import URLSafeSerializer
import secrets
import os, httpx

from rich.console import Console

console = Console()

# Variables
router = APIRouter()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

WEB_REDIRECT = os.getenv("WEB_REDIRECT_OAUTH2")
OAUTH2_URI = os.getenv("API_OAUTH2_URL")
OAUTH2_CALLBACK = os.getenv("API_OAUTH2_CALLBACK")

serializer = URLSafeSerializer(secret_key=os.getenv("OAUTH2_SECRET"), salt="oauth2-dashboard")

# Authentication

@router.get("/auth/login")
async def login():
    url = OAUTH2_URI
    return RedirectResponse(url)

@router.get("/auth/callback")
async def login_callback(code: str):
    async with httpx.AsyncClient() as client:
        token_payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': OAUTH2_CALLBACK,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        release = await client.post(url='https://discord.com/api/oauth2/token', data=token_payload, headers=headers)

        if not release.is_success:
            return { "Error" : "Failed to retrieve!"}
        release = release.json()

        authorization_type = release["token_type"]
        authorization_token = release["access_token"]

        user_header = {
            "Authorization": f"{authorization_type} {authorization_token}"
        }

        user_data = await client.get("https://discord.com/api/v10/users/@me", headers=user_header)
        user_data = user_data.json()

        user_id = user_data['id']
        user_avatar = user_data['avatar']

        session_payload = {
            'id': user_id,
            'username': user_data['username'],
            'global_name': user_data['global_name'],
            'avatar': f"https://cdn.discordapp.com/avatars/{user_id}/{user_avatar}.png?size=4096"
        }

        signed = serializer.dumps(session_payload)

        response = RedirectResponse(WEB_REDIRECT)

        response.set_cookie(
            "session",
            signed,
            60*60*24*7,
            httponly=True,
            samesite="lax",
            secure=True
        )

        return response

@router.get("/auth/session")
async def session_callback(request : Request):
    cookie = request.cookies.get('session')

    if cookie is None:
        raise HTTPException(400, detail='Not authenticated')
    
    try:
        user = serializer.loads(cookie)
    except:
        raise HTTPException(400, detail='Unexpected Error')
    
    return user

