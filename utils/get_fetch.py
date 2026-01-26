from discord import Guild, Role
from discord.abc import GuildChannel

async def get_role(guild : Guild, role_id : int) -> Role | None:
    role = guild.get_role(role_id)

    if role is None:
        try:
            role = await guild.fetch_role(role_id)
        except:
            pass

    return role

async def get_channel(guild : Guild, channel_id : int) -> GuildChannel | None:
    channel = guild.get_channel(channel_id)

    if channel is None:
        try:
            channel = await guild.fetch_channel(channel_id)
        except:
            pass

    return channel