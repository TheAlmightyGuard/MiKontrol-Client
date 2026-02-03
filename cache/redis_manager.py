import asyncio
import os
from typing import Optional
from datetime import datetime
from redis import Redis
from models.moderation import ModerationTask
from models.tickets import TicketEntry
from repositories.mod_repo import delete_task, get_redis_task, update_log

from rich.console import Console

redis_client : Optional[Redis] = None
output_scan_proccess = False
console = Console()


async def connect_redis(client):

    from bot.client import MiBotClient
    assert isinstance(client, MiBotClient)

    global redis_client

    redis_client = Redis(host=os.getenv("REDIS_IP"), port=6379, decode_responses=True, password=os.getenv("REDIS_PWRD") if os.getenv("REDIS_PWRD") != "None" else None)

    status = redis_client.ping()  # Test connection

    if status:
        console.log("Connected to Redis successfully.")
        asyncio.create_task(mod_tasks(client))

    else:
        console.log("Failed to connect to Redis.")

def add_task(src: ModerationTask) -> bool:
    
    result = redis_client.zadd(
        name="moderation:expires",
        mapping={
            src.actionId: src.expiresAt.timestamp()
        }
    )

    if result:
        return True
    return False

def remove_task(actionId: str) -> bool:
    count = redis_client.zrem("moderation:expires", actionId)

    if count > 0:
        return True
    else:
        return False

async def mod_tasks(client):

    from bot.client import MiBotClient
    assert isinstance(client, MiBotClient)

    
    console.log("Moderation Worker has been initialized")
    while not client.is_closed():
        
        if output_scan_proccess:
            console.log("[/] REDIS MANAGER: Scanning Redis for expired tasks...")
        current = datetime.now().timestamp()

        score = redis_client.zrangebyscore(
            name="moderation:expires",
            min=0,
            max=current
        )

        if output_scan_proccess:
            console.log(score)

        for id in score:
            document : ModerationTask | None = await get_redis_task(actionId=id)

            if output_scan_proccess:
                console.log(f"[/] REDIS MANAGER: Document for id {id}... {document}")
            if document is None:

                if output_scan_proccess:
                    console.log("[/] REDIS MANAGER: Due to no document found, deleting task from cache...")
                redis_client.zrem("moderation:expires", id)
                continue

            
            guild = await client.fetch_guild(document.guildId)

            if guild is None:
                console.log("Guild not found. Skipping...")
                continue
            
            if document.type == 'T_MUTE':
                member = await guild.fetch_member(document.targetId)
                if member is None:
                    console.log("Member not found. Skipping...")
                    continue

                for roleId in document.listRoles:
                    role = guild.get_role(roleId)

                    if role is not None:
                        await member.add_roles(role)
                    else:
                        console.log("Role not found. Skipping...")

            elif document.type == 'T_BAN':
                user = client.get_user(document.targetId)
                if user is None:
                    try:
                        user = await client.fetch_user(document.targetId)
                    except:
                        console.log(f"User ID [{document.targetId}] not found. Removing clutter...")
                        redis_client.zrem("moderation:expires", document.actionId)
                        continue

                try:
                    await guild.unban(
                        user, 
                        reason = f"Tasked by Redis. Action ID target {id}"
                    )
                except Exception as e:
                    console.log(f"Error found: {e}")
                    continue
            
            await delete_task(actionId=id)
            redis_client.zrem("moderation:expires", document.actionId)
            await update_log(document.actionId, "EXPIRED", 0, "Auto-expired moderation task.")
            console.log(f"[/] REDIS MANAGER: Removing task with actionId: {document.actionId} that expired at {document.expiresAt}")
            


        await asyncio.sleep(5)


def add_agent(src: TicketEntry) -> bool:
    
    result = redis_client.hset(
        "ticketAgent",
        src.ticket_id,
        str(src.agent_role_id)
    )

    if result:
        return True
    return False

def set_agent(
    ticket_id : str,
    assigned_id : int   
) -> bool:
    
    redis_client.hset(
        "ticketAgent",
        ticket_id,
        assigned_id
    )

    return True

def remove_agent(
    ticket_id : str
) -> bool:
    
    result = redis_client.hdel(
        "ticketAgent",
        ticket_id,
    )

    if result:
        return True
    return False

def get_agent(
    ticket_id : str
) -> str | None:
    
    result = redis_client.hget(
        "ticketAgent",
        ticket_id,
    )

    return result