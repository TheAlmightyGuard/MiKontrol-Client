import os

from itsdangerous import URLSafeSerializer

from utils.get_fetch import get_guild, get_user
from bot.instance import client
from fastapi import APIRouter, HTTPException, Request

serializer = URLSafeSerializer(secret_key=os.getenv("OAUTH2_SECRET"), salt="oauth2-dashboard")

router = APIRouter()

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
async def getMutual(request : Request):
    
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
            "id": str(guild.id),
            "icon": guild.icon.url if guild.icon is not None else None
        }
        
        mutualsPayload.append(guildPayload)

        payload['mutual_count'] += 1

    payload['mutual_guilds'] = mutualsPayload

    return payload

@router.get("/user/guild/members")
async def getGuildCount(request : Request):
    
    sessionCookie = request.cookies.get('session')
    guildCookie = request.cookies.get('guild')
    
    try:
        user = serializer.loads(sessionCookie)
    except:
        raise HTTPException(400, detail='Unexpected Error')

    if sessionCookie is None or guildCookie is None:
        raise HTTPException(400, detail='Missing cookies')

    user = await get_user(client, user['id'])
    
    if user is None:
        raise HTTPException(404, detail='No user found')
    
    mutuals = user.mutual_guilds
    
    if len(mutuals) == 0:
        raise HTTPException(404, detail='No mutuals found')
    
    target = None

    for guild in mutuals:
        if guild.id == int(guildCookie):
            target = guild

    if target is None:
        raise HTTPException(400, detail="Target Guild is not within your mutuals")
    
    roleMemberCount = await target.role_member_counts()

    rolePayloads = []

    for role, count in roleMemberCount.items():
        rolePayloads.append({
            'name': role.name,
            'amount': count
        })

    payload = {
        'by_role': rolePayloads,
        'total': guild.member_count
    }

    return payload

@router.get("/user/guild")
async def getGuild(request : Request):

    sessionCookie = request.cookies.get('session')
    guildCookie = request.cookies.get('guild')
    
    try:
        user = serializer.loads(sessionCookie)
    except:
        raise HTTPException(400, detail='Unexpected Error')

    if sessionCookie is None or guildCookie is None:
        raise HTTPException(400, detail='Missing cookies')

    user = await get_user(client, user['id'])
    
    if user is None:
        raise HTTPException(404, detail='No user found')
    
    mutuals = user.mutual_guilds
    
    if len(mutuals) == 0:
        raise HTTPException(404, detail='No mutuals found')
    
    target = None

    for guild in mutuals:
        if guild.id == int(guildCookie):
            target = guild

    if target is None:
        raise HTTPException(400, detail="Target Guild is not within your mutuals")
    
    
    payload = {
        'name': target.name,
        'id': str(target.id),
        'icon': target.icon.url if target.icon is None else None
    }

    return payload