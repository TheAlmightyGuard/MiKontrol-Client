from typing import Optional
from models.base import BaseModelConfig, MiBaseModel

class Guild(MiBaseModel):
    serverId: int
    locale: str = "en-US"
    premiumLevel: int = 0

class GuildUpdate(BaseModelConfig):
    locale: Optional[str] = None
    premiumLevel: Optional[int] = None

class GuildPreferences(MiBaseModel):
    serverId: int

    # Moderation
    prefix: str = "!"
    mutedRole: Optional[int] = None
