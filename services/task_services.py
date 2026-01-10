from models.moderation import ModerationTask
from repositories.mod_repo import post_mute, post_ban
from cache.redis_manager import add_task

async def create_mute_task(task: ModerationTask):

    if task.expiresAt is not None:
        redis_ok = add_task(task)
        if not redis_ok:
            return
        
    await post_mute(task)
    
    

async def create_ban_task(task: ModerationTask):

    if task.expiresAt != None:
        redis_ok = add_task(task)
        if not redis_ok:
            return
        await post_ban(task)

