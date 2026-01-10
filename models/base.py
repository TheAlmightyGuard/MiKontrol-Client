from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

class BaseModelConfig(BaseModel):
    model_config = {
    "populate_by_name": True,
    "extra": "forbid",
    }

class MiBaseModel(BaseModelConfig):
    createdAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updatedAt: Optional[datetime] = None
    expiresAt: Optional[datetime] = None


