from models.guild import Guild, GuildPreferences, GuildPreferredRole
from repositories.guild_repo import guild_create, get_guild, get_guild_preferences

from cache.redis_manager import get_guild_set_roles, set_guild_set_roles

from typing import Literal

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

async def grab_preferred_role(
    guildId: int,
    purpose : Literal['developer', 'moderator', 'muted']
) -> int | None:
    
    result = get_guild_set_roles(purpose, guildId)

    if result is None:
        result = await get_guild_preferences(guildId)

        
        result = result.preferredRoles

        if result is None:
            return None
        
        # Redis Sync
        set_guild_set_roles(result, guildId)

        for preferred in result:
            if preferred.purpose == purpose:
                return preferred.id
            
        return None

    return result.id