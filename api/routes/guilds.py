from utils.get_fetch import get_guild, get_user
from bot.instance import client
from fastapi import APIRouter

router = APIRouter()

@router.get("/guild/{guild_id}")
async def getGuild(guild_id : str):

    guild = await get_guild(client, int(guild_id))

    if guild is None:
        return { "Error": "Guild not found"}
    
    payload = {
        'serverId' : guild.id,
        'icon' : guild.icon.url if guild.icon is not None else None,
        'mfaLevel' : guild.mfa_level,
        'owner': guild.owner.id,
        'member_count' : guild.member_count,
        'boostLevel' : guild.premium_tier
    }

    return payload

@router.get("/user/{user_id}")
async def getUser(user_id : str):
    
    user = await get_user(client, int(user_id))
    
    if user is None:
        return { "Error": "User not found"}
    
    payload = {
        'name': user.name,
        'id': user.id,
        'avatar': user.avatar.url if user.avatar is not None else None,
        'bot' : user.bot
    }
    
    return payload


@router.get("/user/{user_id}/mutuals")
async def getUser(user_id : str):
    
    user = await get_user(client, int(user_id))
    
    if user is None:
        return { "Error": "User not found"}
    
    mutuals = user.mutual_guilds
    
    if len(mutuals) == 0:
        return { "Error": "No mutuals founds"}
    
    payload = {
        'mutual_guilds' : [],
        'mutual_count': 0
    }

    mutualsPayload = []

    for guild in mutuals:
        guildPayload = {"name": guild.name, "id": guild.id}
        
        mutualsPayload.append(guildPayload)

        payload['mutual_count'] += 1

    payload['mutual_guilds'] = mutualsPayload

    return payload