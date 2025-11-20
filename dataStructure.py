from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class User(BaseModel):
    id: Optional[int] = None
    name: str
    icon: Optional[str] = None

class PremiumUsers(BaseModel):
    amount: int
    level: int

class Guild(BaseModel):
    serverId: int
    memberCount: int
    owner: User
    premiumUsers: PremiumUsers
    textChannelCount: int
    voiceChannelCount: int
    vanityUrl: Optional[str] = None
sample = {
    'serverId': 12,
    'memberCount': 12,
    'owner': {
        'id': 12,
        'name': "12",
        'icon': "212"
    },
    'premiumUsers': {
        'amount': 12,
        'level': 12
    },
    'textChannelCount': 12,
    'voiceChannelCount': 12,
    'vanityUrl': "heh"
}