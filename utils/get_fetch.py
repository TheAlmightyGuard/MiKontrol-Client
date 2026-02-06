from discord import Guild, Role, User, Member
from discord.abc import GuildChannel
from discord.ext.commands import Bot

async def get_role(guild : Guild, role_id : int | None) -> Role | None:

    if role_id is not None:
        role = guild.get_role(role_id)

        if role is None:
            try:
                role = await guild.fetch_role(role_id)
            except:
                pass

        return role
    else:
        return None

async def get_channel(guild : Guild, channel_id : int) -> GuildChannel | None:
    channel = guild.get_channel(channel_id)

    if channel is None:
        try:
            channel = await guild.fetch_channel(channel_id)
        except:
            pass

    return channel

async def get_guild(client : Bot, guild_id : int) -> Guild | None:
    guild = client.get_guild(guild_id)

    if guild is None:
        try:
            guild = await client.fetch_guild(guild_id)
        except:
            pass

    return guild

async def get_user(client : Bot, userId : int) -> User | None:
    user = client.get_user(userId)

    if user is None:
        try:
            user = await client.fetch_user(userId)
        except:
            pass

    return user

async def get_member(guild : Guild, userId : int) -> Member | None:
    member = guild.get_member(userId)

    if member is None:
        try:
            member = await guild.fetch_member(userId)
        except:
            pass

    return member

