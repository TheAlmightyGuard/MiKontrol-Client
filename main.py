import asyncio
import discord
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import bson
from pymongo import ReturnDocument

from dataStructure import Guild

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# MongoDB
uri = "mongodb+srv://mikoto_Access:ianlourd15@mikontrol.ud3peyc.mongodb.net/?appName=MiKontrol"
mongoclient = MongoClient(uri, server_api=ServerApi('1'))

# FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Discord
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/guild/{guild_id}")
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
    

@app.get("/user/{user_id}")
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


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message : discord.Message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        guildComponent = message.guild

        try:
            cluster = mongoclient["mikontrol"]["guilds"]
            guild = Guild.model_validate({
                'serverId': guildComponent.id,
                'memberCount': guildComponent.member_count,
                'owner': {
                    'id': guildComponent.owner_id,
                    'name': guildComponent.owner.name,
                    'icon': guildComponent.owner.avatar.url if guildComponent.owner.avatar is not None else None
                },
                'premiumUsers': {
                    'amount': guildComponent.premium_subscription_count,
                    'level': guildComponent.premium_tier
                },
                'textChannelCount': len(guildComponent.text_channels),
                'voiceChannelCount': len(guildComponent.voice_channels),
                'vanityUrl': guildComponent.vanity_url
            })

            guild = guild.model_dump()

            print(guild)
            document = cluster.find_one( filter={"serverId" : message.guild.id} )
            
            if (document is None):
                document = cluster.insert_one(guild)
            else:
                document = cluster.replace_one({"serverId" : guildComponent.id}, replacement=guild)

            print(document)
        except Exception as e:
            print(e)


async def run_discord_bot():
    try:
        mongoclient.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")

        # Use the proper way to run the Discord client
        await client.start("MTQzNzYwMjAyNDkxNjEyNzc4NA.GLwEYC.xHTslMSRWU14HFROxkacgtydAWZbOwVxCcW8vU")
    except Exception as e:
        print(f"Discord bot error: {e}")

asyncio.create_task(run_discord_bot())

# uvicorn main:app --host 0.0.0.0 --port 10000