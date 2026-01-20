from models.tickets import TicketEntry
from repositories.ticket_repo import post_ticket, assign_ticket, close_ticket

async def ticket_create(
    ticket_id: str,
    author_id: int,
    ticket_channel: int,
    ticket_category: int
) -> bool:
    
    entry = TicketEntry(
        ticket_id=ticket_id,
        author_id=author_id,
        assigned_staff=None,
        ticket_channel_id=ticket_channel,
        ticket_category_id=ticket_category,
        priority="Low",
        status="OPEN",
    )

    return await post_ticket(entry)

async def ticket_assign(
    ticket_id : str,
    assigned_id : int   
) -> bool:
    
    await assign_ticket(
        ticket_id=ticket_id,
        assigned_id=assigned_id
    )

    return

async def ticket_close(
    ticket_id: str,
    interaction_user: int | None,
    reason : str
) -> bool:
    
    return await close_ticket(
        ticket_id=ticket_id,
        interaction_user=interaction_user,
        reason=reason
    )