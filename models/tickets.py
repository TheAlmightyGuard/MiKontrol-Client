from datetime import datetime
from models.base import MiBaseModel, BaseModelConfig
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
        "IN_PROGRESS",
        "RESOLVED",
        "EXPIRED",
        "CLOSED"
    ] = "OPEN"

    closed_at : Optional[datetime] = None
    closed_by : Optional[int] = None
    closed_reason : Optional[str] = None


class TicketModalSelectOption(BaseModelConfig):
    title: str
    description: str
    value: Optional[str] = None

class TicketModalField(BaseModelConfig):
    title: str
    description: Optional[str] = None
    component : Literal["TextInput", "UserSelect", "RoleSelect", "ChannelSelect", "Select"] = ""
    textStyle: Literal["short", "paragraph", "long"] = "short"
    max_length : Optional[int] = None
    selectOptions : Optional[list[TicketModalSelectOption]] = None
    required: bool

class TicketModalTemplate(BaseModelConfig):
    title: str
    description: str
    agent_id: int # Agent ID is just the role ID for the role to ping
    fields : list[TicketModalField]

