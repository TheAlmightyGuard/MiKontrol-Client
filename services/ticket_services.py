from models.tickets import TicketEntry

async def ticket_create(
    ticket_id: str,
    author_id: int
):
    entry = TicketEntry(
        ticket_id=ticket_id,
        author_id=author_id,
        assigned_staff=None

    )