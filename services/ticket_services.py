from models.tickets import TicketEntry
from repositories.ticket_repo import post_ticket, assign_ticket, close_ticket, get_ticket
from cache.redis_manager import add_agent, set_agent, remove_agent, get_agent

async def ticket_create(
    ticket_id: str,
    ticket_type: str,
    guild_id: int,
    author_id: int,
    ticket_channel: int,
    ticket_category: int,
    agent_role_id: int
) -> bool:
    
    entry = TicketEntry(
        guild_id=guild_id,
        ticket_type=ticket_type,
        ticket_id=ticket_id,
        author_id=author_id,
        agent_user_id=None,
        agent_role_id=agent_role_id,
        ticket_channel_id=ticket_channel,
        ticket_category_id=ticket_category,
        priority="Low",
        status="OPEN",
    )

    redis_ok = add_agent(entry)

    if not redis_ok:
        return False

    return await post_ticket(entry)

async def ticket_assign(
    ticket_id : str,
    assigned_id : int   
) -> bool:
    
    redis_ok = set_agent(ticket_id, assigned_id)

    if not redis_ok:
        return False
    
    return await assign_ticket(
        ticket_id=ticket_id,
        assigned_id=assigned_id
    )

async def ticket_close(
    ticket_id: str,
    interaction_user: int | None,
    reason : str
) -> bool:
    
    redis_ok = remove_agent(ticket_id)

    if not redis_ok:
        return False
    
    return await close_ticket(
        ticket_id=ticket_id,
        interaction_user=interaction_user,
        reason=reason
    )

async def ticket_pull(
    ticket_id: str
) -> str | None:
    
    redis_ok = get_agent(ticket_id)

    if redis_ok is not None:
        return redis_ok
    
    ticket = await get_ticket(ticket_id)

    return ticket.assigned_staff
