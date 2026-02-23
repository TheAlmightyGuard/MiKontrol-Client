# FastAPI
from discord.ext import commands
from fastapi import APIRouter
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

def set_client(discord_client : commands.Bot):
    global client
    client = discord_client

@router.get("/")
def read_root():
    return {"Hello": "World"}

@router.get("/guild/{guild_id}")
async def getGuildData(guild_id : str):

    try:
        guild = client.get_guild(int(guild_id))

        if not guild:
            return {"error": "Guild not found"}
        
        webhooks = await guild.webhooks()
        invitesComponent = await guild.invites()

        invites = []
        roles = []
        rolesComponent = guild.roles

        textChannelCount = 0
        voiceChannelCount = 0
        
        for invite in invitesComponent:
            invites.append({
                "inviter": {
                    "name": invite.inviter.name,
                    "id": invite.inviter.id
                },
                "link": invite.url,
                "expiresAt": invite.expires_at.timestamp(),
                "channelTarget": {
                    "id": invite.channel.id,
                    "name": invite.channel.name
                },
                "channelType": invite.channel.type.name,
                "uses": invite.uses,
                "maxUses": invite.max_uses
            })

        for role in rolesComponent:
            roles.append({
                "id": role.id,
                "name": role.name
            })

        for channel in guild.text_channels:
            if (channel.type.name == "text"):
                textChannelCount = textChannelCount + 1
            elif (channel.type.name == "voice"):
                voiceChannelCount = voiceChannelCount + 1

        guildData = {
            "guildSettings" : {
                "server_id": guild.id,
                "icon" : guild.icon.url if guild.icon != None else "https://placehold.co/70",
                "mfaLevel": guild.mfa_level.value,
                "webhooks" : {
                    "amount": len(webhooks),
                    "data": webhooks
                }
            },
            "owner": guild.owner.name,
            "members": guild.member_count,
            "textChannelCount": textChannelCount,
            "voiceChannelCount": voiceChannelCount,
            "premiumUsers": {
                "amount": guild.premium_subscription_count,
                "level": guild.premium_tier
            },
            "vanity": guild.vanity_url,
            "invites": {
                "amount": len(invites),
                "data": invites
            },
            "roles" : {
                "amount": len(roles),
                "data": roles
            }
        }

        return guildData
    except Exception as e:
        return {"First throw": "ahh"}
    

@router.get("/user/{user_id}")
async def getGuildData(user_id : str):
    
    try:
        guilds = client.get_user(int(user_id)).mutual_guilds

        if not guilds:
            return {"error": "Guild  or User not found"}
        
        response = []
        user = client.get_user(user_id)

        for guild in guilds:
            
            guildData = {
                "id": guild.id,
                "name": guild.name,
                "icon": guild.icon if guild.icon is None else "https://placehold.co/512",
                "banner": guild.banner if guild.banner is None else "https://placeholder.co/960x540",
                "owner": guild.owner_id == user
            }

            response.append(guildData)

        return response
    except Exception as e:
        return {"First throw": "ahh"}


# Below is reimagined version:

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

        session_payload = {
            'id': user_data['id'],
            'username': user_data['username'],
            'global_name': user_data['global_name'],
            'avatar': user_data['avatar'],
        }

        signed = serializer.dumps(session_payload)

        response = RedirectResponse(WEB_REDIRECT)

        response.set_cookie(
            "session",
            signed,
            60*60*24*7,
            httponly=True,
            samesite="none",
            secure=True
        )

        return response

        



