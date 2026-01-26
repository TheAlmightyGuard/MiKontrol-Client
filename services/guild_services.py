from models.guild import Guild, GuildPreferences
from repositories.guild_repo import guild_create, get_guild, get_guild_preferences

async def guild_join(
    serverId: int,
    locale: str = "en-US",
    premiumLevel: int = 0
):
    guild = Guild(
        serverId=serverId,
        locale=locale,
        premiumLevel=premiumLevel
    )

    created = await guild_create(guild)

    return created

async def grab_guild(
    serverId: int
):
    return await get_guild(serverId)

async def grab_guild_config(
    serverId: int
) -> GuildPreferences:
    return await get_guild_preferences(serverId)