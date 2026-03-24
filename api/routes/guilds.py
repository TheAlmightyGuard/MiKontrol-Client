import os

from itsdangerous import URLSafeSerializer
from collections import Counter

from utils.get_fetch import get_guild, get_user
from bot.instance import client
from fastapi import APIRouter, HTTPException, Request

import discord

serializer = URLSafeSerializer(secret_key=os.getenv("OAUTH2_SECRET"), salt="oauth2-dashboard")

router = APIRouter()

async def getUserFromSession(request : Request) -> discord.User:
    cookie = request.cookies.get('session')

    if cookie is None:
        raise HTTPException(400, detail='No cookies found')
    
    try:
        user = serializer.loads(cookie)
    except:
        raise HTTPException(400, detail='Unexpected Error')
    
    user = await get_user(client, user['id'])
    
    if user is None:
        raise HTTPException(404, detail='No user found')
    
    return user

async def getGuildFromCookie_Restricted(request : Request, user : discord.User) -> discord.Guild:
    cookie = request.cookies.get('guild')

    for guild in user.mutual_guilds:
        if guild.id == int(cookie):
            target = guild

    if target is None:
        raise HTTPException(400, detail="Target Guild is not within your mutuals")
    
    return target

async def getChannelsBreakdown(guild : discord.Guild):


    channel_counts = Counter(type(channel).__name__ for channel in guild.channels)

    result = [
        {
            "name": channel_type, 
            "amount": count
        }

        for channel_type, count in channel_counts.items()
    ]

    return result

@router.get("/user/")
async def getUser(request: Request):
    
    user = await getUserFromSession(request)

    payload = {
        'name': user.name,
        'id': user.id,
        'avatar': user.avatar.url if user.avatar is not None else None,
        'bot' : user.bot
    }
    
    return payload


@router.get("/user/mutuals")
async def getMutual(request : Request):
    
    user = await getUserFromSession(request)
    
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
            "icon": guild.icon.url if guild.icon is not None else None,
            'channels' : await getChannelsBreakdown(guild),
            'owner': {
                'name': guild.owner.name,
                'id': guild.owner_id,
                'avatar': guild.owner.avatar.url if guild.owner.avatar is not None else None,
                'bot': guild.owner.bot
            },
            'totalMembers': guild.member_count,
            'createdAt': guild.created_at.timestamp(),
            'nsfw_level': guild.nsfw_level.value
        }
        
        mutualsPayload.append(guildPayload)

        payload['mutual_count'] += 1

    payload['mutual_guilds'] = mutualsPayload

    return payload

@router.get("/user/guild/members")
async def getGuildCount(request : Request):
    
    user = await getUserFromSession(request)
    target = await getGuildFromCookie_Restricted(request, user)
    
    roleMemberCount = await target.role_member_counts()

    rolePayloads = []

    for role, count in roleMemberCount.items():
        rolePayloads.append({
            'name': role.name,
            'amount': count
        })

    payload = {
        'by_role': rolePayloads,
        'total': target.member_count
    }

    return payload