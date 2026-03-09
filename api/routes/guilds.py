import os

from itsdangerous import URLSafeSerializer

from utils.get_fetch import get_guild, get_user
from bot.instance import client
from fastapi import APIRouter, HTTPException, Request

serializer = URLSafeSerializer(secret_key=os.getenv("OAUTH2_SECRET"), salt="oauth2-dashboard")

router = APIRouter()

@router.get("/guild/{guild_id}")
async def getGuild(guild_id : str):

    guild = await get_guild(client, int(guild_id))

    if guild is None:
        raise HTTPException(404, detail='No guild found')
    
    payload = {
        'serverId' : guild.id,
        'icon' : guild.icon.url if guild.icon is not None else None,
        'mfaLevel' : guild.mfa_level,
        'owner': guild.owner.id,
        'member_count' : guild.member_count,
        'boostLevel' : guild.premium_tier
    }

    return payload

@router.get("/user/")
async def getUser(request: Request):
    
    cookie = request.cookies.get('session')
    
    try:
        user = serializer.loads(cookie)
    except:
        raise HTTPException(400, detail='Unexpected Error')

    if cookie is None:
        raise HTTPException(400, detail='No cookies found')

    user = await get_user(client, user['id'])
    
    if user is None:
        raise HTTPException(404, detail='No user found')
    
    payload = {
        'name': user.name,
        'id': user.id,
        'avatar': user.avatar.url if user.avatar is not None else None,
        'bot' : user.bot
    }
    
    return payload


@router.get("/user/mutuals")
async def getUser(request : Request):
    
    cookie = request.cookies.get('session')
    
    try:
        user = serializer.loads(cookie)
    except:
        raise HTTPException(400, detail='Unexpected Error')

    if cookie is None:
        raise HTTPException(400, detail='No cookies found')

    user = await get_user(client, user['id'])
    
    if user is None:
        raise HTTPException(404, detail='No user found')
    
    mutuals = user.mutual_guilds
    
    if len(mutuals) == 0:
        raise HTTPException(404, detail='No mutuals found')
    
    payload = {
        'mutual_guilds' : [],
        'mutual_count': 0
    }

    mutualsPayload = []

    for guild in mutuals:
        guildPayload = {
            "name": guild.name, 
            "id": guild.id,
            "icon": guild.icon.url if guild.icon is not None else None
        }
        
        mutualsPayload.append(guildPayload)

        payload['mutual_count'] += 1

    payload['mutual_guilds'] = mutualsPayload

    return payload
