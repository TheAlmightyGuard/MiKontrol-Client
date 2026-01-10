from datetime import datetime
from typing import Literal, Optional
from models.moderation import WarningEntry, ModerationLog, ModerationTask
from repositories.mod_repo import post_warn, delete_warn, post_log, get_warns, get_active_task, get_active, delete_task, update_log
from services.task_services import create_mute_task, create_ban_task
from cache.redis_manager import remove_task


async def add_warning(
    actionId: str,
    guildId: int,
    targetId: int,
    moderatorId: int,
    reason: str
):

    warning = WarningEntry(
        actionId=actionId,
        guildId=guildId,
        targetId=targetId,
        moderatorId=moderatorId,
        reason=reason
    )
    
    # Post warning entry to database
    await post_warn(warning)

    await add_moderation_log(
        actionId=actionId,
        guildId=guildId,
        type="WARN",
        reason=reason,
        targetId=targetId,
        status="ACTIVE",
        moderatorId=moderatorId
    )

async def remove_warning(
    actionId: str,
    guildId: int,
    moderatorId: int,
    reason: str,
) -> WarningEntry | None:

    deleted = await delete_warn(actionId, guildId, moderatorId, reason)

    if deleted is None:
        return None
    
    await update_log(actionId, "REVOKED", moderatorId, reason)

    return deleted

async def list_warnings(
    serverId: int,
    userId: int
) -> list[WarningEntry]:

    warnings = await get_warns(
        serverId=serverId,
        userId=userId
    )

    return warnings


async def add_mute(
    actionId: str,
    guildId: int,
    type: Literal["T_MUTE", "MUTE"],
    targetId: int,
    moderatorId: int,
    listRoles: list[int],
    expiresAt: datetime | None,
    reason: str
):

    task_entry = ModerationTask(
        actionId=actionId,
        guildId=guildId,
        type=type,
        targetId=targetId,
        listRoles=listRoles,
        expiresAt=expiresAt,
        reason=reason
    )

    await create_mute_task(task_entry)

    await add_moderation_log(
        actionId=actionId,
        guildId=guildId,
        type=type,
        reason=reason,
        targetId=targetId,
        moderatorId=moderatorId,
        status="ACTIVE",
        expiresAt=expiresAt
    )

async def remove_mute(
    userId: int,
    guildId: int,
    moderatorId: int,
    reason: str
) -> ModerationTask | None:
    
    log = await get_active_task(userId, guildId, ["MUTE", "T_MUTE"])

    if log is None:
        return None
    
    await delete_task(log.actionId)

    # Grab task from redis and remove if log states it is temp.
    if log.type == 'T_MUTE':
        result = remove_task(log.actionId)
        
        if not result:
            print("A temporary mute was not found in redis, continue...")
            return None
        
        await delete_task(
            actionId=log.actionId
        )
        
    await update_log(log.actionId, "REVOKED", moderatorId, reason)

    return log
    

async def add_ban(
    actionId: str,
    guildId: int,
    type: Literal["BAN", "T_BAN"],
    moderatorId: int,
    targetId: int,
    expiresAt: datetime | None,
    reason: str    
):
    task_entry = ModerationTask(
        actionId=actionId,
        guildId=guildId,
        type=type,
        targetId=targetId,
        expiresAt=expiresAt,
        reason=reason
    )

    await create_ban_task(task_entry)

    await add_moderation_log(
        actionId=actionId,
        guildId=guildId,
        type=type,
        reason=reason,
        targetId=targetId,
        moderatorId=moderatorId,
        status="ACTIVE",
        expiresAt=expiresAt
    )   

async def remove_ban(
    userId: int,
    guildId: int,
    moderatorId: int,
    reason: str
) -> ModerationLog | None:
    
    log = await get_active(userId, guildId, ["BAN", "T_BAN"])

    if log is None:
        return None
    
    # Grab task from redis and remove if log states it is temp.
    if log.type == 'T_BAN':
        result = remove_task(log.actionId)
        
        if not result:
            print("A temporary ban was not found in redis, continue...")
            return None
        
        await delete_task(
            actionId=log.actionId
        )
        
    await update_log(log.actionId, "REVOKED", moderatorId, reason)

    return log

async def add_moderation_log(
    actionId: str,
    guildId: int,
    type: Literal["WARN", "MUTE", "T_MUTE", "KICK", "BAN", "T_BAN", "REM_WARN"],
    status: Literal["ACTIVE", "REVOKED", "EXPIRED", "ONCE"],
    reason: str,
    targetId: int,
    moderatorId: int,
    expiresAt: Optional[datetime] = None
):

    log_entry = ModerationLog(
        actionId=actionId,
        guildId=guildId,
        type=type,
        reason=reason,
        targetId=targetId,
        moderatorId=moderatorId,
        status=status,
        expiresAt=expiresAt
    )

    created = await post_log(log_entry)

    return created
