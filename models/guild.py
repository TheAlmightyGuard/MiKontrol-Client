from typing import Optional, Literal
from models.base import BaseModelConfig, MiBaseModel
from models.tickets import TicketModalTemplate

class Guild(MiBaseModel):
    serverId: int
    locale: str = "en-US"
    premiumLevel: int = 0

class GuildUpdate(BaseModelConfig):
    locale: Optional[str] = None
    premiumLevel: Optional[int] = None

class GuildPreferredRole(BaseModelConfig):
    purpose: Literal["developer", "moderator", "muted"]
    id: int

class GuildPreferences(MiBaseModel):
    serverId: int

    # Moderation
    prefix: str = "!"

    # Tickets
    ticket_category : Optional[int] = 0
    custom_tickets: Optional[list[TicketModalTemplate]] = None

    # Roles
    preferredRoles: list[GuildPreferredRole] = None

