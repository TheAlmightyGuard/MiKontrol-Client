# FastAPI
from discord.ext import commands
from fastapi import APIRouter

# FastAPI
router = APIRouter()

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
