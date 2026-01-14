from datetime import datetime
from models.base import MiBaseModel
from typing import Optional, Literal


class TicketEntry(MiBaseModel):
    ticket_id: str
    author_id: int
    assigned_staff: Optional[int] = None
    ticket_channel_id: int
    ticket_category_id: Optional[int] = None
    
    # State
    priority: Literal["Low", "Medium", "High"] = "Low"
    status: Literal[
        "OPEN",
        "IN_PROGRESS"
        "RESOLVED",
        "EXPIRED",
        "CLOSED"
    ] = "OPEN"

    closed_at : datetime
    closed_by : int
    closed_reason : str