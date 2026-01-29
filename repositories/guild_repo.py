from database.mongo import get_db
from models.guild import Guild, GuildPreferences, GuildUpdate

async def get_guild(serverId: int) -> Guild | None:

    db = get_db()

    collection = db.get_collection("guilds")

    if collection is None:
        raise ValueError("Collection 'guilds' does not exist.")
    
    guild = await collection.find_one({"serverId": serverId})
    
    if guild is None:
        return None
    
    guild.pop("_id", None)
    return Guild(**guild)

async def get_guild_preferences(serverId: int) -> GuildPreferences:

    db = get_db()

    collection = db.get_collection("guild_settings")

    if collection is None:
        raise ValueError("Collection 'guild_settings' does not exist.")
    
    guild = await collection.find_one({"serverId": serverId})
    
    if guild is None:
        return await guild_create_config(serverId)
    
    guild.pop("_id", None)
    return GuildPreferences(**guild)

async def get_all_guild_settings() -> list[GuildPreferences]:

    db = get_db()

    collection = db.get_collection("guild_settings")

    if collection is None:
        raise ValueError("Collection 'guild_settings' does not exist.")
    
    guild_settings : list[GuildPreferences] = []

    async with collection.find(
        {}
    ) as cursor:
        async for document in cursor:
            document.pop("_id", None)
            guild_settings.append(GuildPreferences(**document))        

    if len(guild_settings) == 0:
        return None
    else:
        return guild_settings

async def guild_create_config(serverId: int) -> GuildPreferences:

    db = get_db()

    collection = db.get_collection("guild_settings")

    if collection is None:
        raise ValueError("Collection 'guild_settings' does not exist.")


    new = GuildPreferences(
        serverId=serverId
    )

    await collection.update_one(
        {'serverId' : serverId},
        {'$setOnInsert': new.model_dump()},
        upsert=True
    )

    return new

async def guild_create(src: Guild) -> bool:

    db = get_db()

    collection = db.get_collection("guilds")

    if collection is None:
        raise ValueError("Collection 'guilds' does not exist.")

    insert = await collection.update_one(
        {'serverId' : src.serverId},
        {'$setOnInsert': src.model_dump()},
        upsert=True
    )

    await guild_create_config(src.serverId)

    return insert.did_upsert



async def guild_update(serverId, src: GuildUpdate) -> bool:

    db = get_db()
    
    collection = db.get_collection("guilds")

    if collection is None:
        raise ValueError("Collection 'guilds' does not exist.")
    
    update = await collection.update_one(
        {'serverId' : serverId}, 
        {'$set': src.model_dump(exclude_none=True)}
    )

    return update.modified_count > 0