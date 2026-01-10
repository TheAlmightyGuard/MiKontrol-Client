from typing import Literal, Optional
from models.base import MiBaseModel
from datetime import datetime

class ModerationLog(MiBaseModel):
    actionId: str
    guildId: int
    type: Literal["WARN", "MUTE", "T_MUTE", "KICK", "BAN", "T_BAN", "UNMUTE", "UNBAN", "REM_WARN"]
    status: Literal["REVOKED", "ACTIVE", "EXPIRED", "ONCE"] = "ACTIVE"
    targetId: int | None = None
    reason: str
    moderatorId: int
    revoked_by: Optional[int] = None
    revoked_at: Optional[datetime] = None
    revoked_reason: Optional[str] = "No reason provided."
    

class WarningEntry(MiBaseModel):
    actionId: str
    guildId: int
    targetId: int
    moderatorId: int
    reason: str
    status: Literal["REVOKED", "ACTIVE", "EXPIRED"] = "ACTIVE"
    revoked_by: Optional[int] = None
    revoked_at: Optional[datetime] = None
    revoked_reason: Optional[str] = "No reason provided."

class ModerationTask(MiBaseModel):
    actionId: str
    guildId: int
    type: Literal["T_BAN", "T_MUTE", "MUTE", "BAN"]
    targetId: int
    listRoles: Optional[list[int]] = None
    reason: str