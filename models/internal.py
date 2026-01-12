from pydantic import BaseModel


class CogModel(BaseModel):
    commandName: str
    filePath: str
    status: bool
    error: str | None = None
