from pydantic import BaseModel


class ConfDto(BaseModel):
    dernier_import: str | None = None
