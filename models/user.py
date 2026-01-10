from base import BaseModelConfig
from guild import Guild

from typing import Optional
from discord import Role

class UserBaseModel(BaseModelConfig):
    avatarUrl: Optional[str] = None
    userId: int
    global_name: str

class UserUpdate(BaseModelConfig):
    avatarUrl: Optional[str] = None
    global_name: Optional[str] = None



class GuildUser(UserBaseModel):
    nickname: Optional[str] = None
    mutual_guilds: Optional[list[Guild]] = None

class GuildUserUpdate(BaseModelConfig):
    nickname: Optional[str] = None
    mutual_guilds: Optional[list[Guild]] = None


class GuildUserRoles(UserBaseModel):
    listRoles: list[Role]
