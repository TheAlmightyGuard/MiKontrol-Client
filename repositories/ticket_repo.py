from datetime import datetime
from typing import Literal
from database.mongo import get_db
from models.tickets import TicketEntry
from rich.console import Console

console = Console()

async def post_ticket(src: TicketEntry) -> bool:
    db = get_db()

    collection = db.get_collection("tickets")

    if collection is None:
        console.log("Error. Collection 'tickets' not found!")
        return False
    
    result = await collection.insert_one(src.model_dump())

    return result.inserted_id is not None

async def assign_ticket(ticket_id: str, assigned_id: int) -> None:

    db = get_db()

    collection = db.get_collection("tickets")

    if collection is None:
        console.log("Error. Collection 'tickets' not found!")
        return False
    
    result = await collection.find_one_and_update(
        {
            "ticket_id": ticket_id, 
        },
        {
            "$set" : {
                "assigned_staff": assigned_id,
                "status": "IN_PROGRESS",
                "updatedAt": datetime.now()
            }
        },
        upsert=False
    )

    if result is None:
        return None
    
    result.pop("_id", None)

    return TicketEntry(**result)


async def close_ticket(ticket_id: str, interaction_user : int | None, reason : str) -> bool:
    db = get_db()

    collection = db.get_collection("tickets")
    collection_archive = db.get_collection("archive_tickets")

    if (collection is None) or (collection_archive is None):
        console.log("Error. Collection 'tickets' not found!")
        return

    result = await collection.find_one_and_delete(
        {
            "ticket_id": ticket_id
        }
    )

    if result is not None:
        result.pop("_id", None)

        archive = TicketEntry(**result)

        archive.status = "CLOSED"
        archive.closed_at = datetime.now()
        archive.closed_by = interaction_user
        archive.closed_reason = reason

        await collection_archive.insert_one(
            archive.model_dump()
        )
    return result is not None

async def get_ticket(ticket_id: str) -> TicketEntry:
    db = get_db()

    collection = db.get_collection("tickets")

    if collection is None:
        console.log("Error. Collection 'tickets' not found!")
        return False
    
    result = await collection.find_one(
        {
            "ticket_id": ticket_id, 
        },
    )

    if result is None:
        return None
    
    result.pop("_id", None)

    return TicketEntry(**result)

async def get_all_tickets() -> list[TicketEntry] | None:
    db = get_db()

    collection = db.get_collection("tickets")

    if collection is None:
        console.log("Error. Collection 'tickets' not found!")
        return

    tickets : list[TicketEntry] = []

    async with collection.find(
        {}
    ) as cursor:
        async for document in cursor:
            document.pop("_id", None)
            tickets.append(TicketEntry(**document))        

    if len(tickets) == 0:
        return None
    else:
        return tickets