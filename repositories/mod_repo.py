from datetime import datetime
from typing import Literal
from database.mongo import get_db
from models.moderation import WarningEntry, ModerationLog, ModerationTask

async def post_warn(src: WarningEntry) -> bool:

    db = get_db()

    collection = db.get_collection("warn_entries")

    if collection is None:
        raise ValueError("Collection 'warn_entries' does not exist.")
    
    insert = await collection.insert_one(src.model_dump())

    return insert.inserted_id is not None

async def delete_warn(actionId: str, serverId: int, moderatorId: int, reason: str) -> WarningEntry | None:

    db = get_db()
    collection = db.get_collection("warn_entries")

    if collection is None:
        raise ValueError("Collection 'warn_entries' does not exist.")

    delete_result = await collection.find_one_and_update({
        "actionId": actionId,
        "guildId": serverId
    }, {
            "$set": {
                "status": "REVOKED",
                "revoked_by": moderatorId,
                "revoked_at": datetime.now(),
                "revoked_reason": reason
            },
        }, upsert=False
    )

    if delete_result is None:
        return None
    
    delete_result.pop('_id', None)


    return WarningEntry(**delete_result)


async def get_warns(
    serverId: int,
    userId: int
) -> list[WarningEntry]:
    
    db = get_db()
    collection = db.get_collection("warn_entries")

    if collection is None:
        raise ValueError("Collection 'warn_entries' does not exist.")
    
    results : list[WarningEntry] = []

    cursor = collection.find({
        "guildId": serverId,
        "targetId": userId,
        "status": "ACTIVE"
    })

    async for document in cursor:
        document.pop("_id", None)
        results.append(WarningEntry(**document))

    if len(results) == 0:
        return None
    return results



async def post_mute(src: ModerationTask) -> bool:
    db = get_db()
    collection = db.get_collection("moderation_tasks")

    if collection is None:
        raise ValueError("Collection 'moderation_tasks' does not exist.")
    

    result = await collection.insert_one(src.model_dump())

    return result.inserted_id is not None



async def delete_task(actionId: str = None) -> ModerationTask | None:
    db = get_db()

    collection = db.get_collection("moderation_tasks")


    if collection is None:
        raise ValueError("Collection 'moderation_tasks' does not exist.")

    result = await collection.find_one_and_delete({
        "actionId": actionId
    })

    if result is None:
        return None

    
    result.pop('_id', None)


    return ModerationTask(**result)

async def delete_mute(actionId: str = None, userId: int = 0, guildId: int = 0) -> ModerationTask | None:
    db = get_db()

    collection = db.get_collection("moderation_tasks")


    if collection is None:
        raise ValueError("Collection 'moderation_tasks' does not exist.")

    result = None

    if actionId is None:
        
        result = await collection.find_one_and_delete({
            "targetId": userId,
            "guildId": guildId
        })

    else:
        result = await collection.find_one_and_delete({
            "actionId": actionId
        })

    if result is None:
        return None
    
    result.pop('_id', None)

    return ModerationTask(**result)



async def post_ban(src: ModerationTask) -> bool:
    db = get_db()
    collection = db.get_collection("moderation_tasks")

    if collection is None:
        raise ValueError("Collection 'moderation_tasks' does not exist.")
    
    result = await collection.insert_one(src.model_dump())

    return result.inserted_id is not None



async def get_redis_task(actionId: str) -> ModerationTask | None:
    db = get_db()
    collection = db.get_collection("moderation_tasks")

    if collection is None:
        raise ValueError("Collection 'moderation_tasks' does not exist.")
    
    result = await collection.find_one({
        "actionId": actionId
    })

    if result is None:
        return None
    
    result.pop("_id", None)
    return ModerationTask(**result)

async def get_active(userId: int, guildId: int, query : list[str]) -> ModerationLog | None:
    db = get_db()
    collection = db.get_collection("moderation_logs")

    if collection is None:
        raise ValueError("Collection 'moderation_logs' does not exist.")

    result = await collection.find(
        {
            "targetId": userId,
            "guildId": guildId,
            "status": "ACTIVE",
            "type": { "$in": query }
        },
    ).sort("createdAt", -1).limit(1).to_list(length=1)


    if len(result) == 0:
        return None
    
    result = result[0]
    result.pop('_id', None)

    return ModerationLog(**result)

async def get_active_task(userId: int, guildId: int, query : list[str]) -> ModerationTask | None:
    db = get_db()
    collection = db.get_collection("moderation_tasks")

    if collection is None:
        raise ValueError("Collection 'moderation_tasks' does not exist.")

    result = await collection.find(
        {
            "targetId": userId,
            "guildId": guildId,
            "type": { "$in": query }
        },
    ).sort("createdAt", -1).limit(1).to_list(length=1)


    if len(result) == 0:
        return None
    
    result = result[0]
    result.pop('_id', None)

    return ModerationTask(**result)



async def post_log(src: ModerationLog) -> bool:
    db = get_db()
    collection = db.get_collection("moderation_logs")

    if collection is None:
        raise ValueError("Collection 'moderation_logs' does not exist.")
    
    insert = await collection.insert_one(src.model_dump())

    return insert.inserted_id is not None

async def update_log(actionId: str, status: Literal["REVOKED", "EXPIRED"], revoked_by: int, revoked_reason: str) -> None:
    db = get_db()

    # Disable 'active' from log
    collection = db.get_collection("moderation_logs")
    if collection is None:
        raise ValueError("Collection 'moderation_logs' does not exist.")
    
    await collection.find_one_and_update(
        {
            "actionId": actionId
        },
        {
            "$set": {
                "status": status,
                "revoked_by": revoked_by,
                "revoked_at": datetime.now(),
                "revoked_reason": revoked_reason,
            }
        },
        upsert=False
    )