from models.moderation import ModerationTask
from models.tickets import TicketEntry
from repositories.mod_repo import post_mute, post_ban
from repositories.ticket_repo import get_all_tickets
from repositories.guild_repo import get_all_guild_settings
from utils.get_fetch import get_guild, get_channel
from cache.redis_manager import add_task, add_agent
from discord.ext.commands import Bot

from rich.console import Console

console = Console()

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

async def sync_ticket_channels(client : Bot) -> bool:

    # DATABASE -> DISCORD:
    # 1. Grab all tickets in the database
    # 2. Run with client to make sure channels are found within their respective guilds via ticket data. 
    #     Otherwise, delete entry.
    tickets : list[TicketEntry] = []

    tickets = await get_all_tickets()

    if tickets is not None:

        for ticket in tickets:

            guild = await get_guild(client, ticket.guild_id)

            if guild is None:
                continue

            channel = await get_channel(guild, ticket.ticket_channel_id)

            if channel is None:
                continue

            try:
                await channel.delete(f"Syncing... Ticket '{ticket.ticket_channel_id}' does not exist in database")
            except:
                continue


    # DISCORD -> DATABASE:
    # * Only works if ticket channels are under a category
    # 0. Gets guild list from guild_settings
    # 1. Grab all ticket names under the ticket category
    # 2. Run to make sure channels exist within the database. Otherwise, delete channel.

    preferences = await get_all_guild_settings()

    for preference in preferences:

        if preference.ticket_category is None:
            continue

        guild = await get_guild(client, preference.serverId)


        if guild is None:
            continue

        channels = guild.channels

        for channel in channels:

            target_category = channel.category_id

            if target_category is None:
                continue


            if (tickets is None) and (target_category == preference.ticket_category):
                await channel.delete(reason="SYNCING... Ticket was not existent in database")
                continue
            
                
            if preference.ticket_category == target_category:

                is_found = any(ticket.ticket_id == channel.name for ticket in tickets)
                
                if not(is_found):
                    await channel.delete(reason="SYNCING... Ticket was not existent in database")
